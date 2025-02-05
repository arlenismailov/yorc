from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('room/', views.chat_room, name='chat_room'),
] 