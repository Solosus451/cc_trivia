from django.urls import path
from . import views

app_name = 'trivia'

urlpatterns = [
    path('register/', views.register_view, name='register'),  # Ruta para el registro
    path('', views.home, name='home'),
    path('instructions/', views.instructions, name='instructions'),
    path('game/', views.trivia_game, name='game'),
    path('end_game/', views.end_game, name='end_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]