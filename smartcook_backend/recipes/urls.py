from django.urls import path
from . import views

urlpatterns = [
    path('food/', views.food_upload_view, name='food_upload'),
    path('search/', views.search_recipe, name='search_recipe'),
    path('recipes/<str:pk>/', views.recipe_detail_view, name='recipe_detail'),
    path('cart/<str:pk>/', views.cart_view, name='cart'),
    path('add-to-cart/<str:pk>/', views.add_to_cart, name='add_to_cart'),
    path('api/detect/', views.detect_ingredients, name='detect_ingredients'),
]

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# 개발 서버에서 media 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)