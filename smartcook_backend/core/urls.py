from django.urls import path
from . import views
from .views import signup

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path('', views.main_page, name='mainpage'),
]
