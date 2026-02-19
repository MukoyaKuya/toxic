from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('music/', views.music, name='music'),
    path('music/<int:album_id>/', views.album_detail, name='album_detail'),
    path('music/list/', views.music_list, name='music_list'),
    path('tour/', views.tour, name='tour'),
    path('contact/', views.contact, name='contact'),
]
