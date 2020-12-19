from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('second_page.html', views.second_page, name='second_page'),
    path('third_page/', views.third_page, name='third_page'),
    path('image_page/', views.image_page, name='page_with_image'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

