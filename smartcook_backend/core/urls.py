from django.urls import path
from . import views
from .views import signup
from django.contrib.auth.views import LogoutView
from core.views import save_voice_name

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("", views.main_page, name="mainpage"),

    path("menu2/", views.menu2_view, name="menu2"),

    path("logout/", LogoutView.as_view(), name="logout"),
    path("upload/", views.upload_page, name="upload"),
    path("live/", views.live_page, name="live_page"),
    path("mypage/", views.menu2_view, name="mypage"),
    path("save-voice/", save_voice_name, name="save_voice"),
    path("menu2/", views.menu2_view, name="menu2"),
    path("save-preferences/", views.save_preferences, name="save_preferences"),
    path("change-password/", views.change_password, name="change_password"),

]