from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from api.views import *

app_name = "api"

urlpatterns = [
    path('tournaments/', tournament_list, name='tournaments'),
    path('tournaments/<str:tournament>/games/', tournament_games, name='tournament_games'),
    path('tournaments/<str:tournament>/standings/', tournament_standings, name='tournament_standings'),
    path('tournaments/<str:tournament>/stats/', tournament_stats, name='tournament_stats'),
    path('tournaments/<str:tournament>/next_players/', tournament_next_players, name='next_players'),
    path('tournaments/<str:tournament>/<int:game>/', game_info, name='game_info'),
    path('tournaments/<str:tournament>/<int:game>/game_last_round/', game_last_round, name='game_last_round'),
    path('players/', player_list, name='players'),
    path('rounds/', round_list, name='rounds'),
]