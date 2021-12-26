from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.views.generic.base import RedirectView

from . import views

app_name = "web"

urlpatterns = [
    path('', RedirectView.as_view(url='/tournaments/', permanent=False)),
    path('tournaments/', views.tournaments, name='tournaments'),
    path('tournaments/<int:tournament>/', views.TournamentView.as_view(), name='tournament'),
    path('tournaments/<int:tournament>/<int:game>/', views.GameView.as_view(), name='game'),
]