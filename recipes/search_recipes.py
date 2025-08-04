import json

with open("recipes/data/all_recipes_merged.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

keyword = input(" 검색할 요리명/재료: ").strip().lower()
results = [
    r for r in recipes
    if keyword in r.get("title", "").lower() or keyword in " ".join(r.get("ingredients", [])).lower()
]

for i, r in enumerate(results[:5], 1):
    print(f"\n📌 [{i}] {r['title']}")
    print(" 재료:", ", ".join(r['ingredients'][:5]), "...")
    print(" 조리 1단계:", r['steps'][0] if r['steps'] else "없음")
    print(" 이미지:", r['image'])
