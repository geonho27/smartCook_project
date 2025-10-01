import json
import base64
import asyncio
import logging
import sys
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor
from channels.generic.websocket import AsyncWebsocketConsumer
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import platform
import os
import torch   # 👈 추가 필요

# ---------------- UTF-8 로깅 설정 ----------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
logger.addHandler(handler)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=1)  # GPU inference 전용

# ---------------- 클래스 이름/색상 ----------------
HANGUL_NAMES = {
    0: '오이', 1: '소고기', 2: '브로콜리', 3: '양배추', 4: '당근',
    5: '계란', 6: '상추', 7: '양파', 8: '돼지고기', 9: '파',
    10: '새우', 11: '시금치'
}

FIXED_COLORS = {
    0: (0, 0, 255), 1: (0, 255, 0), 2: (255, 0, 0), 3: (0, 255, 255),
    4: (255, 0, 255), 5: (255, 255, 0), 6: (128, 0, 128), 7: (0, 128, 128),
    8: (128, 128, 0), 9: (0, 0, 128), 10: (0, 128, 0), 11: (128, 0, 0)
}

# ---------------- 한글 텍스트 그리기 (WSL 친화) ----------------
def put_hangul_text(img, text, pos, font_size=20, color=(0,255,0)):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # 가능한 폰트 경로
    possible_fonts = [
        "fonts/NanumGothic.ttf",  # 프로젝트 내
    ]
    
    font = None
    for f in possible_fonts:
        if os.path.exists(f):
            try:
                font = ImageFont.truetype(f, font_size)
                break
            except:
                continue
    
    if font is None:
        try:
            font_path = "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc"
            font = ImageFont.truetype(font_path,font_size)
        except:
            font = ImageFont.load_default()
    
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# ---------------- 박스 그리기 + Base64 인코딩 ----------------
def annotate_and_encode(img, results, conf_thresh=0.6):
    annotated_img = img.copy()
    frame_detections = []

    for detection in results:
        boxes = detection['boxes']
        confs = boxes[:, 4]
        keep_idx = confs >= conf_thresh
        if keep_idx.sum() == 0:
            continue

        boxes_xyxy = boxes[keep_idx, :4].astype(int)
        boxes_cls = boxes[keep_idx, 5].astype(int)
        boxes_conf = confs[keep_idx]

        for xy, cls_idx, conf in zip(boxes_xyxy, boxes_cls, boxes_conf):
            x1, y1, x2, y2 = xy
            cls_name = HANGUL_NAMES.get(int(cls_idx), str(cls_idx))
            frame_detections.append(f"{cls_name} {conf:.2f}")
            color = FIXED_COLORS.get(int(cls_idx), (0, 255, 0))
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
            annotated_img = put_hangul_text(
                annotated_img, f"{cls_name} {conf:.2f}", (x1, max(y1 - 25, 0)), 20, color
            )

    ret, encoded_img = cv2.imencode('.jpg', annotated_img, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
    if not ret:
        return None, []
    b64_img = base64.b64encode(encoded_img).decode('utf-8')
    img_data_url = 'data:image/jpeg;base64,' + b64_img
    return img_data_url, frame_detections

# ---------------- Optimized YOLO Wrapper ----------------


class YOLO_PT:
    def __init__(self, model_path="best.pt", device=None, imgsz=640, conf_thresh=0.6):
        self.imgsz = imgsz
        self.conf_thresh = conf_thresh

        # CUDA 사용 가능 여부 확인
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.model = YOLO(model_path)
        self.model.to(self.device)
        logger.info(f"[YOLO INIT] device = {self.device}")

    def infer(self, img):
        h0, w0 = img.shape[:2]
        scale = self.imgsz / max(h0, w0)
        img_resized = img.copy() if scale >= 1.0 else cv2.resize(
            img, (int(w0 * scale), int(h0 * scale))
        )

        # ⬇️ 여기서도 self.device 사용하도록 수정
        results = self.model.predict(
            source=img_resized,
            conf=self.conf_thresh,
            imgsz=self.imgsz,
            device=self.device
        )
        output = []

        for r in results:
            if hasattr(r, 'boxes') and r.boxes is not None and len(r.boxes) > 0:
                boxes = r.boxes.xyxy.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy().reshape(-1, 1)
                cls = r.boxes.cls.cpu().numpy().reshape(-1, 1)

                # 좌표 스케일링
                h1, w1 = img_resized.shape[:2]
                boxes[:, [0, 2]] *= (w0 / w1)
                boxes[:, [1, 3]] *= (h0 / h1)

                out_arr = np.hstack([boxes, confs, cls])
                output.append({'boxes': out_arr})

        return output

# ---------------- WebSocket Consumer ----------------
class DetectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            self.model = YOLO_PT(imgsz=640, conf_thresh=0.6)
            logger.info("YOLO 모델 로드 완료")
        except Exception as e:
            logger.error(f"YOLO 모델 로드 실패: {e}")
            await self.close()
            return

        self.frame_queue = asyncio.Queue(maxsize=1)
        self.all_detections = set()
        self.processing = False
        asyncio.create_task(self.inference_loop())

    async def disconnect(self, close_code):
        if hasattr(self, 'all_detections'):
            final_list = list(self.all_detections)
            try:
                await self.send(text_data=json.dumps({'final_detections': final_list}))
            except:
                pass
            if final_list:
                logger.info(f"[최종 검출 재료] {', '.join(final_list)}")
        logger.info("웹소켓 종료됨")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            frame_data = data.get('frame')
            if not frame_data:
                return
            frame_bytes = base64.b64decode(frame_data.split(",")[1])
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if self.frame_queue.full():
                _ = self.frame_queue.get_nowait()
            await self.frame_queue.put(img)
        except Exception as e:
            logger.error(f"프레임 수신 오류: {e}")

    async def inference_loop(self):
        while True:
            img = await self.frame_queue.get()
            if self.processing:
                continue
            self.processing = True
            loop = asyncio.get_running_loop()
            try:
                results = await loop.run_in_executor(executor, self.model.infer, img)
                img_data_url, frame_detections = await asyncio.to_thread(
                    annotate_and_encode, img, results, self.model.conf_thresh
                )
                if img_data_url:
                    try:
                        await self.send(text_data=json.dumps({'image': img_data_url, 'detections': frame_detections}))
                        self.all_detections.update([d.split()[0] for d in frame_detections])
                    except:
                        pass
            except Exception as e:
                logger.error(f"추론 오류: {e}")
            finally:
                self.processing = False
