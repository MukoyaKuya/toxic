from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('music/', views.music, name='music'),
    path('music/<int:album_id>/', views.album_detail, name='album_detail'),
    path('music/list/', views.music_list, name='music_list'),
    path('tour/', views.tour, name='tour'),
    path('contact/', views.contact, name='contact'),
    path('health/', views.health_check, name='health_check'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]
