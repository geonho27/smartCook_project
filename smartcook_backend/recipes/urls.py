from django.urls import path
from . import views

urlpatterns = [
    # 음식 업로드 / 검색
    path("food_upload/", views.food_upload_view, name="food_upload"),
    path("search_recipe/", views.search_recipe, name="search_recipe"),
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
    path("update_selected/", views.update_selected_ingredients, name="update_selected"),
]
