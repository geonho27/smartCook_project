import requests
import json
import time

API_KEY = "975d010697cf4f5a9e7e"
all_recipes = []

# 전체 개수 자동 추출
url = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/COOKRCP01/json/1/1"
res = requests.get(url)
total_count = int(res.json()["COOKRCP01"]["total_count"])
print(f"총 레시피 수: {total_count}")

# 100개 단위로 반복
for start in range(1, total_count+1, 100):
    end = min(start + 99, total_count)
    url = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/COOKRCP01/json/{start}/{end}"
    res = requests.get(url)

    if res.status_code == 200:
        rows = res.json().get("COOKRCP01", {}).get("row", [])
        for r in rows:
            recipe = {
                "id": r.get("RCP_SEQ"),
                "title": r.get("RCP_NM"),
                "ingredients": r.get("RCP_PARTS_DTLS", "").replace('\n', '').split(", "),
                "steps": [
                    r.get(f"MANUAL{i:02d}", "").strip()
                    for i in range(1, 21)
                    if r.get(f"MANUAL{i:02d}", "").strip()
                ],
                "image": r.get("ATT_FILE_NO_MAIN", "")
            }
            all_recipes.append(recipe)
    else:
        print(f"{start}~{end} 실패")

    time.sleep(0.7)   # API 서버에 부담 주지 않게 살짝 대기

with open("recipes/data/cookrcp01.json", "w", encoding="utf-8") as f:
    json.dump(all_recipes, f, ensure_ascii=False, indent=2)

print(f"{len(all_recipes)}개 레시피 저장 완료")
