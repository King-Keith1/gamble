from django.urls import path
from . import views

app_name = 'dice'

urlpatterns = [
    path('', views.index, name='index'),  # Main game page
    path('play/', views.play_game, name='play_game'),  # Handle game submission
]