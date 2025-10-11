from django.urls import path
from recipes.views import tts_view
from . import views
from .views import list_voices_view

urlpatterns = [
    # 음식 업로드 / 검색
    path("food_upload/", views.food_upload_view, name="food_upload"),
    path("search_recipes_by_detected/", views.search_recipes_by_detected, name="search_recipes_by_detected"),

    # 레시피 상세
    path("recipes/<int:pk>/", views.recipe_detail_view, name="recipe_detail"),

    # 장바구니
    path("cart/<int:pk>/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),

    # YOLO 업로드/인식
    path("upload_preview/", views.upload_preview, name="upload_preview"),
    path("api/detect/", views.detect_ingredients, name="detect_ingredients"),
    path("detect/", views.detect_frame, name="detect_frame"),

    # GPT 재랭킹 API
    path("api/rerank/", views.rerank_view, name="rerank"),
    
    # 실시간 탐색용 JSON API
    path("api/recipes/", views.get_recipes_json, name="get_recipes_json"),

    # TTS
    path("tts/", tts_view, name="tts"),
    path("stt/", views.speech_to_text, name="speech_to_text"),
    path("tts/list-voices/", list_voices_view, name="list_voices"),
]
