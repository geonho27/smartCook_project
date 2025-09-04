# recipes/import_recipes.py
import sys
import os
import json
import django
from pathlib import Path

# 현재 파일 = smartCook_project/smartcook_backend/recipes/import_recipes.py
BASE_DIR = Path(__file__).resolve().parent.parent  # smartCook_project/smartcook_backend
sys.path.append(str(BASE_DIR))  # manage.py 있는 위치 추가

# settings.py 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcook_backend.settings")

django.setup()

from recipes.models import Recipe


def import_data():
    json_file_path = os.path.join(BASE_DIR, "recipes", "data", "recipe_data.json")

    if not os.path.exists(json_file_path):
        print(f"오류: {json_file_path} 파일을 찾을 수 없습니다.")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:
        recipes_data = json.load(f)

    Recipe.objects.all().delete()
    print("기존 레시피 데이터를 모두 삭제했습니다.")

    for recipe_data in recipes_data:
        try:
            cleaned_ingredients = [
                item.replace("구매", "").replace("\n", " ").strip()
                for item in recipe_data.get("ingredients", [])
            ]
            cleaned_steps = [
                item.replace("\n", " ").strip()
                for item in recipe_data.get("steps", [])
            ]

            Recipe.objects.create(
                id=str(recipe_data["id"]),
                title=recipe_data["title"],
                image_url=recipe_data["image"],
                ingredients=cleaned_ingredients,
                steps=cleaned_steps,
            )
            print(f"'{recipe_data['title']}' 레시피를 성공적으로 저장했습니다.")
        except KeyError as e:
            print(f"필수 키({e}) 누락 → {recipe_data.get('title', '제목 없음')}")
            continue


if __name__ == "__main__":
    import_data()
