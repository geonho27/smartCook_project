import json, os, requests, ast
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe


def food_upload_view(request):
    recipes = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("food_name")
        json_path = os.path.join(settings.BASE_DIR, "recipes", "data", "recipe_data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for recipe in data:
            if query.strip() in recipe["title"]:
                recipes.append(recipe)

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
        json_path = os.path.join(settings.BASE_DIR, "recipes", "data", "recipe_data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for recipe in data:
            if query.strip() in recipe["title"]:
                recipes.append(recipe)

    return render(request, "upload.html", {
        "recipes": recipes if recipes else None,
        "query": query,
        "hasRecipes": bool(recipes)
    })


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


# 장바구니 추가
def add_to_cart(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    selected = request.POST.getlist("ingredient")  # 체크된 재료들

    cart = request.session.get("cart", {})

    if pk not in cart:
        cart[pk] = {
            "title": recipe.title,
            "ingredients": []
        }

    for ing in selected:
        if ing not in cart[pk]["ingredients"]:
            cart[pk]["ingredients"].append(ing)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart", pk=pk)


# 장바구니 보기
# views.py - cart_view
def cart_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    cart = request.session.get("cart", {})

    # ✅ 쿼리스트링에서 extra 가져오기
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
    ingredients = [ing.split()[0] for ing in recipe_cart["ingredients"] if ing.strip()]

    return render(request, "cart.html", {
        "recipe": recipe,
        "ingredients": ingredients,
    })



# upload

import os
from uuid import uuid4
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

# YOLO 모델은 한번만 로드
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


# 간단 한-영 매핑(데이터셋 클래스명에 맞춰 자유롭게 추가/수정)
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
}


def upload_preview(request):
    return render(request, "upload_preview.html")


@require_POST
def detect_ingredients(request):
    """이미지 업로드 받아 YOLO로 인식 → 한국어 이름+신뢰도 반환, 주석 이미지 저장"""
    file = request.FILES.get("image")
    if not file:
        return JsonResponse({"ok": False, "error": "image 파일이 필요합니다."}, status=400)

    # 업로드 저장
    upload_dir = settings.MEDIA_ROOT / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.jpg"
    src_path = upload_dir / filename
    with open(src_path, "wb+") as dst:
        for chunk in file.chunks():
            dst.write(chunk)

    # OpenCV로 읽기
    data = np.frombuffer(open(src_path, "rb").read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return JsonResponse({"ok": False, "error": "이미지 해석 실패"}, status=400)

    # YOLO 추론
    model = _get_yolo()
    res = model.predict(img, conf=0.25, imgsz=800)[0]

    # 박스 → 클래스/신뢰도 집계(중복 클래스는 최댓값으로)
    items = {}
    for b in res.boxes:
        name_en = res.names[int(b.cls)]
        conf = float(b.conf)
        items[name_en] = max(items.get(name_en, 0.0), conf)

    items_list = [
        {"name_en": k, "name_ko": KO_MAP.get(k, k), "score": round(v, 3)}
        for k, v in items.items()
    ]

    # 주석 이미지 저장
    ann_dir = settings.MEDIA_ROOT / "annotated"
    ann_dir.mkdir(parents=True, exist_ok=True)
    ann_path = ann_dir / filename
    annotated = res.plot()  # BGR ndarray
    cv2.imwrite(str(ann_path), annotated)
    ann_url = settings.MEDIA_URL + f"annotated/{filename}"

    return JsonResponse({"ok": True, "items": items_list, "annotated_url": ann_url})