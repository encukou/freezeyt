from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('second_page.html', views.second_page, name='second_page'),
    path('third_page/', views.third_page, name='third_page'),
    path('image_page/', views.image_page, name='page_with_image'),
]
