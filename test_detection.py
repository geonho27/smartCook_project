import os
import sys
import random
import cv2
import matplotlib.pyplot as plt
from yolo import FoodIngredientsDetector

def test_detection():
    """훈련된 모델로 이미지 감지 테스트"""
    
    # 감지기 초기화
    data_yaml = 'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/data.yaml'
    model_path = 'food_detection_results/food_ingredients_model/weights/best.pt'
    
    detector = FoodIngredientsDetector(data_yaml, model_path)
    
    # 모델 로드
    if not detector.load_trained_model(model_path):
        print("모델 로드 실패!")
        return
    
    # 훈련 이미지 폴더에서 랜덤으로 이미지 선택
    train_images_dir = 'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/train/images'
    all_images = [f for f in os.listdir(train_images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    # 랜덤으로 5개 이미지 선택
    selected_images = random.sample(all_images, min(5, len(all_images)))
    
    print("=== 음식 재료 감지 테스트 시작 ===\n")
    print(f"선택된 이미지: {selected_images}\n")
    
    # 결과를 저장할 리스트
    results = []
    
    for i, image_name in enumerate(selected_images, 1):
        image_path = os.path.join(train_images_dir, image_name)
        print(f"테스트 {i}: {image_name}")
        print("-" * 50)
        
        try:
            # 이미지 감지
            detections = detector.detect_image(image_path, conf_threshold=0.25, save_result=True)
            
            if detections:
                print(f"✅ 감지 성공: {len(detections)}개의 음식 재료 발견")
                for det in detections:
                    print(f"   - {det['class_name']}: {det['confidence']:.3f}")
            else:
                print("❌ 감지 실패: 음식 재료를 찾지 못했습니다")
            
            # 결과 저장
            results.append({
                'image_path': image_path,
                'image_name': image_name,
                'detections': detections
            })
                
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
        
        print("\n")
    
    # 결과 시각화
    visualize_results(results)
    
    print("=== 테스트 완료 ===")
    print("감지 결과 이미지는 'detection_results' 폴더에 저장되었습니다.")

def visualize_results(results):
    """감지 결과를 시각화"""
    if not results:
        return
    
    # matplotlib 한글 폰트 설정 (Windows)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 결과 이미지들을 그리드로 표시
    n_results = len(results)
    cols = min(3, n_results)
    rows = (n_results + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
    if rows == 1:
        axes = [axes] if cols == 1 else axes
    else:
        axes = axes.flatten()
    
    for i, result in enumerate(results):
        if i >= len(axes):
            break
            
        ax = axes[i]
        
        # 원본 이미지 로드
        image = cv2.imread(result['image_path'])
        if image is not None:
            # BGR을 RGB로 변환
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 이미지 표시
            ax.imshow(image_rgb)
            ax.set_title(f"{result['image_name']}\n감지된 객체: {len(result['detections'])}개", fontsize=10)
            
            # 감지 결과 표시
            if result['detections']:
                for det in result['detections']:
                    x1, y1, x2, y2 = det['bbox']
                    class_name = det['class_name']
                    confidence = det['confidence']
                    
                    # 바운딩 박스 그리기
                    rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, 
                                       fill=False, color='red', linewidth=2)
                    ax.add_patch(rect)
                    
                    # 라벨 추가
                    ax.text(x1, y1-5, f"{class_name}: {confidence:.2f}", 
                           color='red', fontsize=8, weight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            ax.axis('off')
        else:
            ax.text(0.5, 0.5, '이미지 로드 실패', ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
    
    # 빈 서브플롯 숨기기
    for i in range(n_results, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('detection_results/visualization_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("시각화 결과가 'detection_results/visualization_results.png'에 저장되었습니다.")

if __name__ == "__main__":
    test_detection() 