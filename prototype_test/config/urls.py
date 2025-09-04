from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_preview, name='upload_preview'),
    path('api/detect/', views.detect_ingredients, name='detect_ingredients'),
]

# 개발 서버에서 media 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
