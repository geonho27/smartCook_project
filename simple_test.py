import os
import sys
from yolo import FoodIngredientsDetector

def simple_test():
    """간단한 이미지 감지 테스트"""
    
    print("=== 음식 재료 감지 테스트 ===\n")
    
    # 감지기 초기화
    data_yaml = 'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/data.yaml'
    model_path = 'food_detection_results/food_ingredients_model/weights/best.pt'
    
    detector = FoodIngredientsDetector(data_yaml, model_path)
    
    # 모델 로드
    if not detector.load_trained_model(model_path):
        print("❌ 모델 로드 실패!")
        return
    
    print("✅ 모델 로드 성공!\n")
    
    while True:
        print("옵션을 선택하세요:")
        print("1. 이미지 경로 직접 입력")
        print("2. 샘플 이미지 테스트")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            # 사용자가 직접 이미지 경로 입력
            image_path = input("이미지 파일 경로를 입력하세요: ").strip()
            
            if not image_path:
                print("경로를 입력해주세요.\n")
                continue
            
            if not os.path.exists(image_path):
                print(f"❌ 파일을 찾을 수 없습니다: {image_path}\n")
                continue
            
            test_image(detector, image_path)
            
        elif choice == '2':
            # 샘플 이미지 테스트
            sample_images = [
                'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/train/images/Apple_1_jpg.rf.b2655f6a1640d9c1a8ecab9d6550e3e6.jpg',
                'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/train/images/Banana_1_jpg.rf.ad30825baf729b4b21496051e0a0bd89.jpg',
                'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/train/images/Carrot_3_jpg.rf.ffea123a2bc7ea6a2dcc8dfde1bdd343.jpg'
            ]
            
            print("\n사용 가능한 샘플 이미지:")
            for i, img in enumerate(sample_images, 1):
                if os.path.exists(img):
                    print(f"{i}. {os.path.basename(img)}")
            
            try:
                sample_choice = int(input("\n테스트할 이미지 번호를 선택하세요 (1-3): "))
                if 1 <= sample_choice <= len(sample_images):
                    selected_image = sample_images[sample_choice - 1]
                    if os.path.exists(selected_image):
                        test_image(detector, selected_image)
                    else:
                        print(f"❌ 샘플 이미지를 찾을 수 없습니다: {selected_image}\n")
                else:
                    print("❌ 잘못된 번호입니다.\n")
            except ValueError:
                print("❌ 숫자를 입력해주세요.\n")
                
        elif choice == '3':
            print("테스트를 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.\n")

def test_image(detector, image_path):
    """이미지 감지 테스트"""
    print(f"\n--- {os.path.basename(image_path)} 테스트 ---")
    
    try:
        # 감지 실행
        detections = detector.detect_image(image_path, conf_threshold=0.25, save_result=True)
        
        if detections:
            print(f"✅ 감지 성공: {len(detections)}개의 음식 재료 발견")
            print("\n감지 결과:")
            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class_name']} (신뢰도: {det['confidence']:.3f})")
        else:
            print("❌ 감지 실패: 음식 재료를 찾지 못했습니다")
        
        print(f"\n감지 결과 이미지가 'detection_results' 폴더에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    simple_test() 