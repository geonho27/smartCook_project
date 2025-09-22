import json, base64, asyncio, logging
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor
from channels.generic.websocket import AsyncWebsocketConsumer
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import torch
# GPU 사용 가능 여부 안전하게 확인
try:
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        print(f"GPU 사용 가능: {device_name}")
    else:
        print("GPU 사용 불가능, CPU 사용")
except Exception as e:
    print(f"GPU 확인 중 오류: {e}")
    cuda_available = False

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=1)  # GPU inference만

HANGUL_NAMES = {
    0:'오이',1:'소고기',2:'브로콜리',3:'양배추',4:'당근',
    5:'계란',6:'상추',7:'양파',8:'돼지고기',9:'파',
    10:'새우',11:'시금치'
}

FIXED_COLORS = {
    0:(0,0,255),1:(0,255,0),2:(255,0,0),3:(0,255,255),
    4:(255,0,255),5:(255,255,0),6:(128,0,128),7:(0,128,128),
    8:(128,128,0),9:(0,0,128),10:(0,128,0),11:(128,0,0)
}

def put_hangul_text(img,text,pos,font_size=20,color=(0,255,0)):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    try:
        font_path = "C:/Windows/Fonts/malgun.ttf"
        font = ImageFont.truetype(font_path,font_size)
    except:
        font = ImageFont.load_default()
    draw.text(pos,text,font=font,fill=color)
    return cv2.cvtColor(np.array(pil_img),cv2.COLOR_RGB2BGR)

def annotate_and_encode(img, results):
    annotated_img = img.copy()
    frame_detections = []
    for detection in results:
        boxes = detection.boxes
        confs = boxes.conf.cpu().numpy()
        keep_idx = confs>=0.5
        if keep_idx.sum()==0: continue
        boxes_xyxy = boxes.xyxy.cpu().numpy()[keep_idx]
        boxes_cls = boxes.cls.cpu().numpy()[keep_idx]
        boxes_conf = confs[keep_idx]
        for xy,cls_idx,conf in zip(boxes_xyxy,boxes_cls,boxes_conf):
            x1,y1,x2,y2=map(int,xy)
            cls_name = HANGUL_NAMES.get(int(cls_idx),str(cls_idx))
            frame_detections.append(f"{cls_name} {conf:.2f}")
            color = FIXED_COLORS.get(int(cls_idx),(0,255,0))
            cv2.rectangle(annotated_img,(x1,y1),(x2,y2),color,2)
            annotated_img = put_hangul_text(annotated_img,f"{cls_name} {conf:.2f}",(x1,y1-25),20,color)
    ret,encoded_img = cv2.imencode('.jpg', annotated_img,[int(cv2.IMWRITE_JPEG_QUALITY),40])
    if not ret: return None, []
    b64_img = base64.b64encode(encoded_img).decode('utf-8')
    img_data_url = 'data:image/jpeg;base64,' + b64_img
    return img_data_url, frame_detections

class DetectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        try:
            # YOLO 모델 로드 (device 파라미터 제거)
            self.model = YOLO('best.pt')
            # CPU 사용으로 설정
            self.model.to('cpu')
            #self.model.to(device = 0, fp16=True) -> gpu 사용할때 이 코드 사용 할것
            logger.info("YOLO 모델 로드 완료")
        except Exception as e:
            logger.error(f"YOLO 모델 로드 실패: {e}")
            await self.close()  # 모델 로딩 실패 시 연결 종료
            return

        self.frame_queue = asyncio.Queue(maxsize=1)
        self.all_detections = set()
        self.processing = False
        asyncio.create_task(self.inference_loop())

    async def disconnect(self, close_code):
        # all_detections 속성이 존재하는지 확인
        if hasattr(self, 'all_detections'):
            final_list = list(self.all_detections)
            try: 
                await self.send(text_data=json.dumps({'final_detections':final_list}))
            except: 
                pass
            if final_list: 
                print(f"[최종 검출 재료] {', '.join(final_list)}")
        else:
            logger.info("모델 로딩 실패로 인한 연결 종료")
        logger.info("웹소켓 종료됨")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            frame_data = data.get('frame')
            if not frame_data: return
            frame_bytes = base64.b64decode(frame_data.split(",")[1])
            np_arr = np.frombuffer(frame_bytes,np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            img_small = cv2.resize(img,(640,360))
            if self.frame_queue.full(): _=self.frame_queue.get_nowait()
            await self.frame_queue.put(img_small)
        except Exception as e:
            logger.error(f"프레임 수신 오류: {e}")

    async def inference_loop(self):
        while True:
            img = await self.frame_queue.get()
            if self.processing: continue
            self.processing = True
            loop = asyncio.get_running_loop()
            try:
                # 모델이 없으면 건너뛰기
                if not hasattr(self, 'model') or self.model is None:
                    logger.error("모델이 로드되지 않음")
                    continue
                # GPU 추론만 executor에서 실행
                results = await loop.run_in_executor(executor, self.model, img)
                # annotation + encode는 별도 쓰레드에서 처리
                img_data_url, frame_detections = await asyncio.to_thread(annotate_and_encode, img, results)
                if img_data_url:
                    try:
                        await self.send(text_data=json.dumps({'image':img_data_url,'detections':frame_detections}))
                        self.all_detections.update([d.split()[0] for d in frame_detections])
                    except: pass
            except Exception as e:
                logger.error(f"추론 오류: {e}")
            finally:
                self.processing = False
