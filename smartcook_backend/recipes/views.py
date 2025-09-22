import os
import json
import requests
from uuid import uuid4
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator   # 페이지네이션 추가
from .models import Recipe

model = YOLO('best.pt')

# 카메라 초기화 (0: 기본 웹캠)
cap = cv2.VideoCapture(0)

@csrf_exempt
def detect_frame(request):
    if request.method == 'POST' and request.FILES.get('frame'):
        file = request.FILES['frame']
        file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        results = model(img)[0]

        # 80% 이상 confidence인 박스만 필터링
        filtered_boxes = []
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf >= 0.6:
                filtered_boxes.append(box)

        results.boxes = filtered_boxes  
        
        annotated_img = results.plot()
        _, buffer = cv2.imencode('.jpg', annotated_img)
        return HttpResponse(buffer.tobytes(), content_type="image/jpeg")
    
    return JsonResponse({"error": "No frame uploaded"}, status=400)


# =========================
# 전역 캐시 및 세션
# =========================
_recipe_cache = None
SESSION_QUERY_KEY = "sc.query"
SESSION_RESULT_IDS_KEY = "sc.result_ids"
SESSION_MODE_KEY = "sc.mode"
SESSION_DETECTED_KEY = "sc.detected"   # ✅ YOLO 인식 재료 저장용

def get_recipes_data():
    """ recipe_data.json 캐싱 """
    global _recipe_cache
    if _recipe_cache is None:
        json_path = os.path.join(settings.BASE_DIR, "recipes", "data", "recipe_data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            _recipe_cache = json.load(f)
    return _recipe_cache

def _index_by_id(data_list):
    return {str(item.get("id")): item for item in data_list}

def _save_session_search(request, *, query: str, mode: str, result_ids: list[int]):
    request.session[SESSION_QUERY_KEY] = query
    request.session[SESSION_MODE_KEY] = mode
    request.session[SESSION_RESULT_IDS_KEY] = list(map(int, result_ids))
    request.session.modified = True

def _load_session_search(request):
    return {
        "query": request.session.get(SESSION_QUERY_KEY, ""),
        "mode": request.session.get(SESSION_MODE_KEY, ""),
        "result_ids": request.session.get(SESSION_RESULT_IDS_KEY, []),
    }

# =========================
# 재료 클리너
# =========================
EXCLUDE_KEYWORDS = ["주재료", "도마", "조리용", "전자레인지", "용기", "그릇", "위생장갑", "구매"]

def clean_ingredients(ingredients):
    cleaned = []
    for ing in ingredients:
        if not ing:
            continue
        text = ing.strip()
        if not text:
            continue
        # 개행/공백 정리
        text = text.replace("\n", " ").replace("\r", " ")
        text = " ".join(text.split())
        # 불필요 단어 제외
        if any(bad in text for bad in EXCLUDE_KEYWORDS):
            continue
        # 재료명만 추출 (첫 단어)
        name = text.split()[0]
        cleaned.append(name)
    return cleaned


# =========================
# 페이지네이션 헬퍼 (6개 단위, 빈자리 없이)
# =========================
def paginate_queryset(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    total_pages = paginator.num_pages

    # 10개 단위 그룹 계산
    page_group = (current_page - 1) // 10
    start_page = page_group * 10 + 1
    end_page = min(start_page + 9, total_pages)
    page_range = range(start_page, end_page + 1)

    return page_obj, paginator, page_range, total_pages


# =========================
# 음식명 검색
# =========================
def food_upload_view(request):
    recipes = []
    query = request.GET.get("q", "").strip()
    sort_option = request.GET.get("sort", "match")

    data = get_recipes_data()

    if query:
        query_ingredients = [q.strip() for q in query.split(",") if q.strip()]
        results = []

        for recipe in data:
            short_ingredients = clean_ingredients(recipe.get("ingredients", []))
            match_count = 0

            if query in recipe.get("title", ""):
                match_count += 2
            ing_match_count = sum(1 for q in query_ingredients if q in short_ingredients)
            match_count += ing_match_count

            if match_count > 0:
                r = dict(recipe)
                r["match_count"] = match_count
                r["ingredient_count"] = len(short_ingredients)
                r["ingredients"] = short_ingredients
                results.append(r)

        if sort_option == "ingredients":
            recipes = sorted(results, key=lambda r: r.get("ingredient_count", 0))
        else:
            recipes = sorted(results, key=lambda r: r.get("match_count", 0), reverse=True)

        # 세션 저장
        _save_session_search(
            request,
            query=query,
            mode="food",
            result_ids=[r.get("id") for r in recipes if r.get("id") is not None],
        )

    # ✅ 재료 없는 레시피는 제외
    valid_recipes = [r for r in recipes if r.get("ingredients")]

    # 페이지네이션 적용
    recipes_page, paginator, page_range, total_pages = paginate_queryset(request, valid_recipes, 6)

    return render(request, "food_upload.html", {
        "recipes": recipes_page,
        "query": query,
        "sort": sort_option,
        "hasRecipes": bool(valid_recipes),
        "paginator": paginator,
        "page_range": page_range,
        "total_pages": total_pages,
    })








# 업로드 이미지 인식
def search_recipes_by_detected(request):
    # 체크박스로 선택된 재료 가져오기
    selected_ingredients = request.GET.getlist("q")

    # 선택 없으면 세션에서 불러오기
    if selected_ingredients:
        detected_ingredients = selected_ingredients
    else:
        detected_ingredients = request.session.get(SESSION_DETECTED_KEY, [])

    sort_option = request.GET.get("sort", "match")

    # "알 수 없음" 제거
    detected_ingredients = [i for i in detected_ingredients if i != "알 수 없음"]

    data = get_recipes_data()
    results = []

    if detected_ingredients:
        for recipe in data:
            recipe_ingredients = clean_ingredients(recipe.get("ingredients", []))
            match_count = sum(1 for item in detected_ingredients if item in recipe_ingredients)

            if match_count > 0:
                r = dict(recipe)
                r["ingredient_count"] = len(recipe_ingredients)
                r["match_count"] = match_count
                r["ingredients"] = recipe_ingredients
                results.append(r)

        # 정렬 로직
        if sort_option == "ingredients":
            # ✅ 재료 적은 순 → ingredient_count 오름차순만 고려
            results = sorted(
                results,
                key=lambda r: r.get("ingredient_count", 0)
            )
        else:
            # ✅ 관련도 순 → match_count 내림차순만 고려
            results = sorted(
                results,
                key=lambda r: r.get("match_count", 0),
                reverse=True
            )

        # 세션 저장
        _save_session_search(
            request,
            query=",".join(detected_ingredients),
            mode="detected",
            result_ids=[r.get("id") for r in results if r.get("id") is not None],
        )

    valid_results = [r for r in results if r.get("ingredients")]

    results_page, paginator, page_range, total_pages = paginate_queryset(request, valid_results, 6)

    # 실시간 탐색에서 호출된 경우 live.html 템플릿 사용
    template_name = "upload.html"  # 기본값
    if request.GET.get('from') == 'live':
        template_name = "live.html"

    return render(request, template_name, {
        "recipes": results_page,
        "query": ", ".join(selected_ingredients) if selected_ingredients else ", ".join(detected_ingredients),
        "query_list": selected_ingredients if selected_ingredients else detected_ingredients,  # 핵심 수정
        "sort": sort_option,
        "hasRecipes": bool(valid_results),
        "paginator": paginator,
        "page_range": page_range,
        "total_pages": total_pages,
        "selected_ingredients": selected_ingredients, 
    })


# =========================
# 레시피 상세 + 유튜브
# =========================
def recipe_detail_view(request, pk):
    data = get_recipes_data()
    recipe = next((r for r in data if str(r.get("id")) == str(pk)), None)
    if not recipe:
        raise Http404("Recipe not found")

    query = request.GET.get("q", "")
    sess = _load_session_search(request)
    if not query and sess["query"]:
        query = sess["query"]

    mode = sess["mode"]

    api_key = settings.YOUTUBE_API_KEY
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": recipe.get("title", ""),
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
        "query": query,
        "mode": mode,
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

    sess = _load_session_search(request)

    return render(request, "cart.html", {
        "recipe": recipe,
        "ingredients": ingredients,
        "search_mode": sess["mode"],
        "search_query": sess["query"],
        "search_sort": request.GET.get("sort", "match"),
    })


# =========================
# YOLO ingredient detection
# =========================
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

    res = model.predict(img, conf=0.25, imgsz=800)[0]

    items = {}
    for b in res.boxes:
        name_en = res.names[int(b.cls)]
        conf = float(b.conf)
        items[name_en] = max(items.get(name_en, 0.0), conf)

    items_list = []
    detected_names = []
    for k, v in items.items():
        name_ko = KO_MAP.get(k.lower(), None)

        if not name_ko:
            continue

        items_list.append({
            "name": name_ko,
            "score": round(v, 3)
        })
        detected_names.append(name_ko)

    request.session[SESSION_DETECTED_KEY] = detected_names
    request.session.modified = True

    ann_dir = settings.MEDIA_ROOT / "annotated"
    ann_dir.mkdir(parents=True, exist_ok=True)
    ann_path = ann_dir / filename
    annotated = res.plot()
    cv2.imwrite(str(ann_path), annotated)
    ann_url = settings.MEDIA_URL + f"annotated/{filename}"

    return JsonResponse({"ok": True, "items": items_list, "annotated_url": ann_url})


# =========================
# GPT 재랭킹
# =========================
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

@csrf_exempt
def get_recipes_json(request):
    """실시간 탐색을 위한 JSON API 엔드포인트"""
    # 체크박스로 선택된 재료 가져오기
    selected_ingredients = request.GET.getlist("q")

    # 선택 없으면 세션에서 불러오기
    if selected_ingredients:
        detected_ingredients = selected_ingredients
    else:
        detected_ingredients = request.session.get(SESSION_DETECTED_KEY, [])

    sort_option = request.GET.get("sort", "match")

    # "알 수 없음" 제거
    detected_ingredients = [i for i in detected_ingredients if i != "알 수 없음"]

    data = get_recipes_data()
    results = []

    if detected_ingredients:
        for recipe in data:
            recipe_ingredients = clean_ingredients(recipe.get("ingredients", []))
            match_count = sum(1 for item in detected_ingredients if item in recipe_ingredients)

            if match_count > 0:
                r = dict(recipe)
                r["ingredient_count"] = len(recipe_ingredients)
                r["match_count"] = match_count
                r["ingredients"] = recipe_ingredients
                results.append(r)

        # 정렬 로직
        if sort_option == "ingredients":
            results = sorted(
                results,
                key=lambda r: r.get("ingredient_count", 0)
            )
        else:
            results = sorted(
                results,
                key=lambda r: r.get("match_count", 0),
                reverse=True
            )

        # 세션 저장
        _save_session_search(
            request,
            query=",".join(detected_ingredients),
            mode="detected",
            result_ids=[r.get("id") for r in results if r.get("id") is not None],
        )

    valid_results = [r for r in results if r.get("ingredients")]
    
    # 최대 6개만 반환 (실시간 탐색용)
    limited_results = valid_results[:6]

    return JsonResponse({
        "recipes": limited_results,
        "query": ", ".join(detected_ingredients),
        "total_count": len(valid_results),
        "has_recipes": bool(valid_results)
    })

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