import os
import cv2
import yaml
import torch
from ultralytics import YOLO
import numpy as np
from pathlib import Path
import argparse

class FoodIngredientsDetector:
    def __init__(self, data_yaml_path, model_path=None):
        """
        음식 재료 감지기 초기화
        
        Args:
            data_yaml_path (str): data.yaml 파일 경로
            model_path (str): 사전 훈련된 모델 경로 (선택사항)
        """
        self.data_yaml_path = data_yaml_path
        self.model_path = model_path
        self.model = None
        self.class_names = []
        self.load_data_config()
        
    def load_data_config(self):
        """data.yaml 파일에서 클래스 정보 로드"""
        with open(self.data_yaml_path, 'r', encoding='utf-8') as f:
            data_config = yaml.safe_load(f)
        
        self.class_names = data_config.get('names', [])
        print(f"로드된 클래스 수: {len(self.class_names)}")
        print(f"클래스 목록: {self.class_names}")
    
    def train_model(self, epochs=100, batch_size=16, imgsz=640):
        """
        YOLO 모델 훈련
        
        Args:
            epochs (int): 훈련 에포크 수
            batch_size (int): 배치 크기
            imgsz (int): 입력 이미지 크기
        """
        print("모델 훈련을 시작합니다...")
        
        # YOLO 모델 초기화
        if self.model_path and os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
            print(f"기존 모델 로드: {self.model_path}")
        else:
            self.model = YOLO('yolov8n.pt')  # 기본 모델 사용
            print("새로운 YOLOv8 모델 초기화")
        
        # 모델 훈련
        results = self.model.train(
            data=self.data_yaml_path,
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            patience=20,
            save=True,
            project='food_detection_results',
            name='food_ingredients_model'
        )
        
        print("훈련 완료!")
        return results
    
    def load_trained_model(self, model_path):
        """훈련된 모델 로드"""
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
            print(f"모델 로드 완료: {model_path}")
            return True
        else:
            print(f"모델 파일을 찾을 수 없습니다: {model_path}")
            return False
    
    def detect_image(self, image_path, conf_threshold=0.25, save_result=True):
        """
        이미지에서 음식 재료 감지
        
        Args:
            image_path (str): 이미지 파일 경로
            conf_threshold (float): 신뢰도 임계값
            save_result (bool): 결과 이미지 저장 여부
            
        Returns:
            list: 감지 결과
        """
        if self.model is None:
            print("모델이 로드되지 않았습니다. 먼저 모델을 로드하세요.")
            return None
        
        # 이미지 감지
        results = self.model(image_path, conf=conf_threshold)
        
        # 결과 처리
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 바운딩 박스 좌표
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # 클래스 정보
                    class_id = int(box.cls[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # 클래스 이름
                    class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                    
                    detection = {
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': [x1, y1, x2, y2]
                    }
                    detections.append(detection)
        
        # 결과 출력
        print(f"\n감지된 음식 재료 수: {len(detections)}")
        for det in detections:
            print(f"- {det['class_name']}: {det['confidence']:.3f}")
        
        # 결과 이미지 저장
        if save_result:
            result_path = self.save_detection_result(image_path, detections)
            print(f"결과 이미지 저장: {result_path}")
        
        return detections
    
    def save_detection_result(self, image_path, detections):
        """감지 결과를 이미지에 그려서 저장"""
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print(f"이미지를 로드할 수 없습니다: {image_path}")
            return None
        
        # 감지 결과 그리기
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            confidence = det['confidence']
            
            # 바운딩 박스 그리기
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # 라벨 텍스트
            label = f"{class_name}: {confidence:.2f}"
            
            # 텍스트 배경
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(image, (int(x1), int(y1) - text_height - 10), 
                         (int(x1) + text_width, int(y1)), (0, 255, 0), -1)
            
            # 텍스트 그리기
            cv2.putText(image, label, (int(x1), int(y1) - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # 결과 저장
        output_dir = "detection_results"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.basename(image_path)
        result_path = os.path.join(output_dir, f"detected_{filename}")
        cv2.imwrite(result_path, image)
        
        return result_path
    
    def evaluate_model(self, data_yaml_path):
        """모델 성능 평가"""
        if self.model is None:
            print("모델이 로드되지 않았습니다.")
            return
        
        print("모델 평가 중...")
        results = self.model.val(data=data_yaml_path)
        
        # 평가 결과 출력
        metrics = results.results_dict
        print(f"\n평가 결과:")
        print(f"mAP50: {metrics.get('metrics/mAP50', 'N/A')}")
        print(f"mAP50-95: {metrics.get('metrics/mAP50-95', 'N/A')}")
        print(f"Precision: {metrics.get('metrics/precision', 'N/A')}")
        print(f"Recall: {metrics.get('metrics/recall', 'N/A')}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='음식 재료 감지 YOLO 모델')
    parser.add_argument('--mode', choices=['train', 'detect', 'evaluate'], 
                       required=True, help='실행 모드')
    parser.add_argument('--data', default='food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/data.yaml',
                       help='data.yaml 파일 경로')
    parser.add_argument('--model', help='모델 파일 경로')
    parser.add_argument('--input', help='입력 이미지 경로')
    parser.add_argument('--epochs', type=int, default=100, help='훈련 에포크 수')
    parser.add_argument('--conf', type=float, default=0.25, help='신뢰도 임계값')
    
    args = parser.parse_args()
    
    # 감지기 초기화
    detector = FoodIngredientsDetector(args.data, args.model)
    
    if args.mode == 'train':
        # 모델 훈련
        detector.train_model(epochs=args.epochs)
        
    elif args.mode == 'detect':
        # 이미지 감지
        if not args.input:
            print("입력 이미지 경로를 지정해주세요.")
            return
        
        if args.model:
            detector.load_trained_model(args.model)
        
        detector.detect_image(args.input, conf_threshold=args.conf)
        
    elif args.mode == 'evaluate':
        # 모델 평가
        if args.model:
            detector.load_trained_model(args.model)
        
        detector.evaluate_model(args.data)

if __name__ == "__main__":
    # 예제 사용법
    print("음식 재료 감지 YOLO 모델")
    print("\n사용법:")
    print("1. 모델 훈련: python yolo.py --mode train")
    print("2. 이미지 감지: python yolo.py --mode detect --input image.jpg --model best.pt")
    print("3. 모델 평가: python yolo.py --mode evaluate --model best.pt")
    print("\n자동으로 훈련을 시작합니다...")
    
    # 자동 훈련 실행
    detector = FoodIngredientsDetector('food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/data.yaml')
    detector.train_model(epochs=50)  # 빠른 테스트를 위해 50 에포크
