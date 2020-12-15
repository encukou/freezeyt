from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('second_page.html', views.second_page, name='second_page'),
]
