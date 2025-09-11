from django.urls import path
from . import views
from .views import signup
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("", views.main_page, name="mainpage"),
    path("menu2/", views.menu2_view, name="menu2"),   # 마이페이지 (POST 저장 지원)
    path("logout/", LogoutView.as_view(), name="logout"),
    path("upload/", views.upload_page, name="upload"),
    path("mypage/", views.mypage_view, name="mypage"),  # 혹시 단순 랜더링용 별도 필요할 경우
]
