import json

with open("recipes/data/popular_recipes.json", "r", encoding="utf-8") as f:
    recipes_10000 = json.load(f)

with open("recipes/data/cookrcp01.json", "r", encoding="utf-8") as f:
    recipes_korea = json.load(f)

merged = recipes_10000 + recipes_korea

with open("recipes/data/all_recipes_merged.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f" 총 {len(merged)}개 레시피 병합 완료")
