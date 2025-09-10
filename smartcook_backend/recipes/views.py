import os
import json
import requests
from uuid import uuid4
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Recipe

# =========================
# 전역 캐시: recipe_data.json
# =========================
_recipe_cache = None

def get_recipes_data():
    """
    recipe_data.json을 한 번만 읽고,
    이후에는 캐싱된 데이터를 반환.
    """
    global _recipe_cache
    if _recipe_cache is None:
        json_path = os.path.join(settings.BASE_DIR, "recipes", "data", "recipe_data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            _recipe_cache = json.load(f)
    return _recipe_cache


# =========================
# 재료 필터링
# =========================
EXCLUDE_KEYWORDS = ["주재료", "도마", "조리용", "전자레인지", "용기", "그릇", "위생장갑", "구매"]

def clean_ingredients(ingredients):
    """
    불필요한 도구/구매 항목을 제외하고
    음식 재료 이름만 반환
    """
    cleaned = []
    for ing in ingredients:
        if not ing.strip():
            continue
        if any(bad in ing for bad in EXCLUDE_KEYWORDS):
            continue
        name = ing.split()[0]  # 첫 단어만 사용
        cleaned.append(name)
    return cleaned


# =========================
# 업로드 / 검색
# =========================
def food_upload_view(request):
    recipes = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("food_name", "").strip()
        data = get_recipes_data()   # JSON 캐싱된 데이터 불러오기

        if query:
            query_ingredients = [q.strip() for q in query.split(",") if q.strip()]
            results = []

            for recipe in data:
                short_ingredients = clean_ingredients(recipe.get("ingredients", []))
                match_count = 0

                # 1) 음식명(title) 매칭
                if query in recipe.get("title", ""):
                    match_count += 2   # 음식명 매칭은 가중치 2

                # 2) 재료명 매칭
                ing_match_count = sum(1 for q in query_ingredients if q in short_ingredients)
                match_count += ing_match_count

                if match_count > 0:
                    recipe["match_count"] = match_count
                    results.append(recipe)

            # match_count 기준 내림차순 정렬
            recipes = sorted(results, key=lambda r: r.get("match_count", 0), reverse=True)

    return render(request, "food_upload.html", {
        "recipes": recipes if recipes else None,
        "query": query,
        "hasRecipes": bool(recipes),
    })



def search_recipe(request):
    recipes = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("food_name")
        data = get_recipes_data()   # ✅ 캐싱된 데이터 사용

        query_ingredients = [q.strip() for q in query.split(",") if q.strip()]

        for recipe in data:
            short_ingredients = clean_ingredients(recipe.get("ingredients", []))
            match_count = sum(1 for q in query_ingredients if q in short_ingredients)

            if match_count > 0:
                recipe["match_count"] = match_count
                recipes.append(recipe)

        recipes.sort(key=lambda r: r.get("match_count", 0), reverse=True)

    return render(request, "upload.html", {
        "recipes": recipes if recipes else None,
        "query": query,
        "hasRecipes": bool(recipes),
    })


# =========================
# 레시피 상세 + 유튜브 영상
# =========================
def recipe_detail_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    api_key = settings.YOUTUBE_API_KEY
    search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": recipe.title,
        "type": "video",
        "maxResults": 3,
        "key": api_key,
    }

    response = requests.get(search_url, params=params).json()
    videos = []
    for item in response.get("items", []):
        videos.append({
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })

    return render(request, "recipe.html", {
        "recipe": recipe,
        "videos": videos,
    })


# =========================
# 장바구니
# =========================
def add_to_cart(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    selected = request.POST.getlist("ingredient")

    cart = request.session.get("cart", {})

    if pk not in cart:
        cart[pk] = {"title": recipe.title, "ingredients": []}

    for ing in selected:
        if ing not in cart[pk]["ingredients"]:
            cart[pk]["ingredients"].append(ing)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart", pk=pk)


def cart_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    cart = request.session.get("cart", {})

    extras = request.GET.get("extra")
    if extras:
        extras = extras.split(",")
        if pk not in cart:
            cart[pk] = {"title": recipe.title, "ingredients": []}
        for ing in extras:
            if ing not in cart[pk]["ingredients"]:
                cart[pk]["ingredients"].append(ing)

        request.session["cart"] = cart
        request.session.modified = True

    recipe_cart = cart.get(pk, {"ingredients": []})
    ingredients = clean_ingredients(recipe_cart["ingredients"])

    return render(request, "cart.html", {
        "recipe": recipe,
        "ingredients": ingredients,
    })


# =========================
# YOLO 업로드 / 인식
# =========================
_yolo_model = None

def _get_yolo():
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        model_path = settings.BASE_DIR / "best.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"YOLO 가중치가 없습니다: {model_path}")
        _yolo_model = YOLO(str(model_path))
    return _yolo_model


KO_MAP = {
    "cucumber": "오이",
    "carrot": "당근",
    "potato": "감자",
    "onion": "양파",
    "tofu": "두부",
    "egg": "달걀",
    "pork": "돼지고기",
    "beef": "소고기",
    "chicken": "닭고기",
    "noodle": "면",
    "kimchi": "김치",
    "tuna": "참치",
    "leek": "대파",
    "pepper": "고추",
    "garlic": "마늘",
    "sesame_oil": "참기름",
    "soy_sauce": "간장",
    "sugar": "설탕",
    "carrots": "당근",
    "tomato": "토마토",
    "broccoli": "브로콜리",
}


def upload_preview(request):
    return render(request, "upload_preview.html")


@require_POST
def detect_ingredients(request):
    """
    이미지 업로드 받아 YOLO로 인식 → 한국어 이름+신뢰도 반환, 주석 이미지 저장
    """
    file = request.FILES.get("image")
    if not file:
        return JsonResponse({"ok": False, "error": "image 파일이 필요합니다."}, status=400)

    upload_dir = settings.MEDIA_ROOT / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.jpg"
    src_path = upload_dir / filename
    with open(src_path, "wb+") as dst:
        for chunk in file.chunks():
            dst.write(chunk)

    data = np.frombuffer(open(src_path, "rb").read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return JsonResponse({"ok": False, "error": "이미지 해석 실패"}, status=400)

    model = _get_yolo()
    res = model.predict(img, conf=0.25, imgsz=800)[0]

    items = {}
    for b in res.boxes:
        name_en = res.names[int(b.cls)]   # YOLO 클래스 이름 (영어)
        conf = float(b.conf)
        items[name_en] = max(items.get(name_en, 0.0), conf)

    # 한국어 변환 후 name 키로 반환
    items_list = []
    for k, v in items.items():
        name_ko = KO_MAP.get(k.lower(), None)  # 소문자 통일
        if not name_ko:
            name_ko = "알 수 없음"  # 기본값
        items_list.append({
            "name": name_ko,
            "score": round(v, 3)
        })

    ann_dir = settings.MEDIA_ROOT / "annotated"
    ann_dir.mkdir(parents=True, exist_ok=True)
    ann_path = ann_dir / filename
    annotated = res.plot()  # BGR ndarray
    cv2.imwrite(str(ann_path), annotated)
    ann_url = settings.MEDIA_URL + f"annotated/{filename}"

    return JsonResponse({"ok": True, "items": items_list, "annotated_url": ann_url})



# =========================
# GPT 재랭킹
# =========================
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt
def rerank_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        candidates = data.get("candidates", [])
        selected = data.get("selected", [])
        cuisines = data.get("cuisines", [])
        spicy = data.get("spicy", 50)

        prompt = f"""
        선택된 재료: {', '.join(selected)}
        선호 음식 분야: {', '.join(cuisines) if cuisines else '무관'}
        선호 매운맛: {spicy}/100
        후보 레시피: {json.dumps(candidates, ensure_ascii=False)}

        후보를 관련성 높은 순으로 정렬해서 JSON 배열로 출력:
        [{{"id": "레시피ID", "score": 0~1, "reason": "이유"}}]
        """

        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 요리 추천 도우미야."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3
        )

        text = res.choices[0].message["content"]
        try:
            ranked = json.loads(text)
        except Exception:
            ranked = []

        return JsonResponse({"recommendations": ranked})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
