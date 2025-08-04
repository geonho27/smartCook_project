import requests
from bs4 import BeautifulSoup
import time
import json

def get_recipe_ids_from_page(page):
    url = f"https://www.10000recipe.com/recipe/list.html?order=reco&page={page}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("ul.common_sp_list_ul.ea4 li a.common_sp_link")
    return [link["href"].split("/")[-1] for link in links if "/recipe/" in link["href"]]

def crawl_recipe_detail(recipe_id):
    url = f"https://www.10000recipe.com/recipe/{recipe_id}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        return {
            "id": recipe_id,
            "title": soup.select_one('.view2_summary h3').text.strip(),
            "ingredients": [i.text.strip() for i in soup.select('.ready_ingre3 ul li')],
            "steps": [s.text.strip() for s in soup.select('.view_step_cont')],
            "image": soup.select_one('.centeredcrop img')['src']
        }
    except Exception as e:
        print(f" {recipe_id} 실패:", e)
        return None

all_ids = set()
for page in range(1, 51):
    all_ids.update(get_recipe_ids_from_page(page))
    time.sleep(1)

recipes = []
for i, rid in enumerate(list(all_ids)[:100], 1):
    print(f" ({i}) {rid}")
    result = crawl_recipe_detail(rid)
    if result: recipes.append(result)
    time.sleep(1)

with open("recipes/data/popular_recipes.json", "w", encoding="utf-8") as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)

print(f" 총 {len(recipes)}개 저장 완료")
