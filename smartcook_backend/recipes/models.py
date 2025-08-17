

from django.db import models

# 1. 사용자 입력 (텍스트 or 이미지 기반 탐색)
class UserInput(models.Model):
    INPUT_TYPE_CHOICES = [
        ('text', '텍스트'),
        ('image', '이미지'),
    ]
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES)
    input_text = models.CharField(max_length=255, blank=True, null=True)
    input_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.input_type} 입력 - {self.uploaded_at.strftime("%Y-%m-%d %H:%M")}'

# 2. 인식된 재료
class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 3. 입력과 인식된 재료 연결 (Many-to-Many)
class RecognizedIngredient(models.Model):
    user_input = models.ForeignKey(UserInput, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient.name} ({self.user_input.id})'

# 4. 카테고리 및 선호도
class Preference(models.Model):
    user_input = models.OneToOneField(UserInput, on_delete=models.CASCADE)
    categories = models.CharField(max_length=255)  # 예: "한식,중식"
    spicy_level = models.IntegerField(default=50)  # 0~100 슬라이더 값

    def __str__(self):
        return f'Preference for {self.user_input.id}'

# 5. 추천된 레시피
class Recipe(models.Model):
    title = models.CharField(max_length=100)
    ingredients = models.TextField()  # 재료 리스트를 문자열로 저장
    instructions = models.TextField()  # 요리 방법
    estimated_time = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)

    def __str__(self):
        return self.title

# 6. 추천 결과 (추천된 레시피와 어떤 입력이 연결됐는지 기록)
class Recommendation(models.Model):
    user_input = models.ForeignKey(UserInput, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recommend {self.recipe.title} for input {self.user_input.id}'
