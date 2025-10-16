from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from recipes import views 

urlpatterns = [
    # 관리자 페이지
    path("admin/", admin.site.urls),
    # path("mainpage/", TemplateView.as_view(template_name="mainpage.html")),
    # path("login/", TemplateView.as_view(template_name="login.html")),
    # path("signup/", TemplateView.as_view(template_name="signup.html")),
    # path("cart/", TemplateView.as_view(template_name="cart.html")),
    # path("menu2/", TemplateView.as_view(template_name="menu2.html")),
    # path("recipe/", TemplateView.as_view(template_name="recipe.html")),
    # path("upload/", TemplateView.as_view(template_name="upload.html")),
    # path("food_upload/", TemplateView.as_view(template_name="food_upload.html")),
    # path("live/", TemplateView.as_view(template_name="live.html"), name="live_page"),

    path("auth/onedrive/callback/", views.onedrive_callback, name="onedrive_callback"),

    path("", include("core.urls")),
    path("", include("recipes.urls")),
    path("", include("django.contrib.auth.urls")),
    path("", include("detector.urls")),
]
