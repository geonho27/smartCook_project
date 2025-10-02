# consumers.py

import cv2
import json
import base64
import asyncio
import logging
import sys
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from channels.generic.websocket import AsyncWebsocketConsumer

# OpenVINO 대신 ultralytics 라이브러리를 직접 사용합니다.
from ultralytics import YOLO

# --- 로깅 설정 ---
logger = logging.getLogger()
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
logger = logging.getLogger(__name__)

# --- 상수 정의 ---
HANGUL_NAMES = {
    0: '오이', 1: '소고기', 2: '브로콜리', 3: '양배추', 4: '당근',
    5: '계란', 6: '상추', 7: '양파', 8: '돼지고기', 9: '파',
    10: '새우', 11: '시금치'
}

# ▼▼▼▼▼ 클래스별 색상 지정 (HEX 코드) ▼▼▼▼▼
# HANGUL_NAMES의 순서(0~11)에 맞춰 각 클래스의 색상을 정의합니다.
CLASS_COLORS = [
    '#FF3838', '#FF9D97', '#FF701F', '#FFB21D', '#CFD231', '#48F28B', '#97FF64',
    '#01FCEF', '#00A9FF', '#0049FF', '#AD46FF', '#FF53B0'
]
# ▲▲▲▲▲ 클래스별 색상 지정 ▲▲▲▲▲


# ▼▼▼▼▼ 여기서 모델의 민감도를 조절할 수 있습니다 ▼▼▼▼▼
CONF_THRESH = 0.6 # 이전 단계에서 0.6로 조정했습니다.
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

# 모델 추론을 위한 스레드 풀
executor = ThreadPoolExecutor(max_workers=1)

# --- WebSocket Consumer ---
class DetectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            # OpenVINO 모델 대신 원본 best.pt 모델을 로드합니다.
            self.model = YOLO("best.pt")
            logger.info("YOLOv8 PyTorch 모델 로드 완료 (best.pt)")
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            await self.close()
            return

        self.frame_queue = asyncio.Queue(maxsize=1)
        self.loop = asyncio.get_running_loop()
        self.all_detections = set()
        
        # 추론 루프를 백그라운드에서 실행
        asyncio.create_task(self.inference_loop())

    async def disconnect(self, close_code):
        if hasattr(self, 'all_detections') and self.all_detections:
            final_list = list(self.all_detections)
            logger.info(f"[최종 검출 재료] {', '.join(final_list)}")
            try:
                await self.send(text_data=json.dumps({'final_detections': final_list}))
            except: pass
        logger.info("웹소켓 종료됨")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            frame_data = data.get('frame')
            if not frame_data: return
            frame_bytes = base64.b64decode(frame_data.split(",")[1])
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if self.frame_queue.full(): await self.frame_queue.get()
            await self.frame_queue.put(img)
        except Exception as e:
            logger.error(f"프레임 수신 오류: {e}")

    async def inference_loop(self):
        while True:
            img = await self.frame_queue.get()
            if img is None: break
            
            # 별도 스레드에서 추론 및 후처리 실행
            await self.loop.run_in_executor(
                executor, self.infer_and_process, img
            )

    def infer_and_process(self, img):
        """
        [동기 함수] 별도 스레드에서 실행됩니다.
        YOLO 모델로 추론하고 결과를 JSON으로 만들어 전송합니다.
        """
        try:
            # YOLO 라이브러리의 predict 함수를 직접 사용. NMS가 내장되어 있음.
            results = self.model.predict(img, conf=CONF_THRESH, verbose=False)

            # 결과가 있는 경우에만 처리
            if results and results[0].boxes:
                boxes = results[0].boxes
                frame_detections_data = []
                unique_detections_in_frame = set()

                for box in boxes:
                    cls_idx = int(box.cls.item())
                    conf = box.conf.item()
                    cls_name = HANGUL_NAMES.get(cls_idx, f"ID:{cls_idx}")
                    xyxy = box.xyxy.cpu().numpy()[0]
                    
                    # ▼▼▼▼▼ 색상 정보 추가 ▼▼▼▼▼
                    # cls_idx에 해당하는 색상을 CLASS_COLORS 리스트에서 가져옵니다.
                    # 만약 cls_idx가 리스트 범위를 벗어나도 오류가 나지 않도록 % 연산자 사용
                    color = CLASS_COLORS[cls_idx % len(CLASS_COLORS)]
                    # ▲▲▲▲▲ 색상 정보 추가 ▲▲▲▲▲

                    frame_detections_data.append({
                        'box': xyxy.tolist(),
                        'label': f"{cls_name} {conf:.2f}",
                        'name': cls_name,
                        'color': color # JSON에 색상 정보 추가
                    })
                    unique_detections_in_frame.add(cls_name)

                if frame_detections_data:
                    self.all_detections.update(unique_detections_in_frame)
                    asyncio.run_coroutine_threadsafe(
                        self.send(text_data=json.dumps({'detections': frame_detections_data})),
                        self.loop
                    )
        except Exception as e:
            logger.error(f"추론/후처리 오류: {e}", exc_info=True)