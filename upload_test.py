import os
import sys
import cv2
import matplotlib.pyplot as plt
from yolo import FoodIngredientsDetector
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class ImageUploadTester:
    def __init__(self):
        """이미지 업로드 테스터 초기화"""
        self.detector = None
        self.current_image_path = None
        self.current_detections = None
        
        # 감지기 초기화
        self.init_detector()
        
        # GUI 초기화
        self.init_gui()
    
    def init_detector(self):
        """YOLO 감지기 초기화"""
        try:
            data_yaml = 'food_ingredients_pj.v2-roboflow-instant-3--eval-.yolov8/data.yaml'
            model_path = 'food_detection_results/food_ingredients_model/weights/best.pt'
            
            self.detector = FoodIngredientsDetector(data_yaml, model_path)
            
            if not self.detector.load_trained_model(model_path):
                print("모델 로드 실패!")
                return False
            
            print("✅ 모델 로드 성공!")
            return True
            
        except Exception as e:
            print(f"❌ 모델 초기화 실패: {str(e)}")
            return False
    
    def init_gui(self):
        """GUI 초기화"""
        self.root = tk.Tk()
        self.root.title("음식 재료 감지 테스터")
        self.root.geometry("800x600")
        
        # 메인 프레임
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = tk.Label(main_frame, text="음식 재료 감지 테스터", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 이미지 업로드 버튼
        upload_btn = tk.Button(button_frame, text="이미지 업로드", 
                              command=self.upload_image, 
                              font=("Arial", 12), bg="#4CAF50", fg="white")
        upload_btn.pack(side=tk.LEFT, padx=5)
        
        # 감지 실행 버튼
        detect_btn = tk.Button(button_frame, text="감지 실행", 
                              command=self.detect_image, 
                              font=("Arial", 12), bg="#2196F3", fg="white")
        detect_btn.pack(side=tk.LEFT, padx=5)
        
        # 결과 저장 버튼
        save_btn = tk.Button(button_frame, text="결과 저장", 
                            command=self.save_result, 
                            font=("Arial", 12), bg="#FF9800", fg="white")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 이미지 표시 영역
        self.image_frame = tk.Frame(main_frame, bg="lightgray")
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 이미지 라벨
        self.image_label = tk.Label(self.image_frame, text="이미지를 업로드하세요", 
                                   font=("Arial", 14))
        self.image_label.pack(expand=True)
        
        # 결과 표시 영역
        result_frame = tk.Frame(main_frame)
        result_frame.pack(fill=tk.X, pady=10)
        
        # 결과 텍스트
        self.result_text = tk.Text(result_frame, height=8, font=("Arial", 10))
        self.result_text.pack(fill=tk.X)
        
        # 스크롤바
        scrollbar = tk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
    
    def upload_image(self):
        """이미지 업로드"""
        file_path = filedialog.askopenfilename(
            title="이미지 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("모든 파일", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"이미지 업로드 완료: {os.path.basename(file_path)}\n")
    
    def display_image(self, image_path):
        """이미지 표시"""
        try:
            # 이미지 로드 및 리사이즈
            image = Image.open(image_path)
            
            # 이미지 크기 조정 (최대 400x400)
            max_size = 400
            width, height = image.size
            if width > max_size or height > max_size:
                ratio = min(max_size/width, max_size/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # PhotoImage로 변환
            photo = ImageTk.PhotoImage(image)
            
            # 라벨 업데이트
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # 참조 유지
            
        except Exception as e:
            self.image_label.config(text=f"이미지 로드 실패: {str(e)}")
    
    def detect_image(self):
        """이미지 감지"""
        if not self.current_image_path:
            messagebox.showwarning("경고", "먼저 이미지를 업로드하세요!")
            return
        
        if not self.detector:
            messagebox.showerror("오류", "모델이 로드되지 않았습니다!")
            return
        
        try:
            # 감지 실행
            self.current_detections = self.detector.detect_image(
                self.current_image_path, 
                conf_threshold=0.25, 
                save_result=True
            )
            
            # 결과 표시
            self.display_results()
            
        except Exception as e:
            messagebox.showerror("오류", f"감지 중 오류 발생: {str(e)}")
    
    def display_results(self):
        """감지 결과 표시"""
        self.result_text.delete(1.0, tk.END)
        
        if not self.current_detections:
            self.result_text.insert(tk.END, "❌ 감지된 음식 재료가 없습니다.\n")
            return
        
        self.result_text.insert(tk.END, f"✅ 감지된 음식 재료: {len(self.current_detections)}개\n\n")
        
        for i, det in enumerate(self.current_detections, 1):
            class_name = det['class_name']
            confidence = det['confidence']
            bbox = det['bbox']
            
            result_line = f"{i}. {class_name}\n"
            result_line += f"   신뢰도: {confidence:.3f}\n"
            result_line += f"   위치: ({bbox[0]:.1f}, {bbox[1]:.1f}) ~ ({bbox[2]:.1f}, {bbox[3]:.1f})\n\n"
            
            self.result_text.insert(tk.END, result_line)
        
        self.result_text.insert(tk.END, "감지 결과 이미지가 'detection_results' 폴더에 저장되었습니다.\n")
    
    def save_result(self):
        """결과 저장"""
        if not self.current_detections:
            messagebox.showwarning("경고", "저장할 결과가 없습니다!")
            return
        
        # 결과를 텍스트 파일로 저장
        save_path = filedialog.asksaveasfilename(
            title="결과 저장",
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(f"음식 재료 감지 결과\n")
                    f.write(f"이미지: {os.path.basename(self.current_image_path)}\n")
                    f.write(f"감지된 객체 수: {len(self.current_detections)}\n\n")
                    
                    for i, det in enumerate(self.current_detections, 1):
                        f.write(f"{i}. {det['class_name']}\n")
                        f.write(f"   신뢰도: {det['confidence']:.3f}\n")
                        f.write(f"   바운딩 박스: {det['bbox']}\n\n")
                
                messagebox.showinfo("성공", f"결과가 저장되었습니다: {save_path}")
                
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류 발생: {str(e)}")
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    print("음식 재료 감지 테스터를 시작합니다...")
    
    app = ImageUploadTester()
    app.run()

if __name__ == "__main__":
    main() 