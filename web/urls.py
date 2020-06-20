from django.urls import path, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.views.generic.base import RedirectView

from web.views import *

app_name = "web"

urlpatterns = [
    path('', RedirectView.as_view(url='/tournaments/', permanent=False)),
    path('tournaments/', TournamentsView.as_view(), name='tournaments'),
    path('tournaments/<slug:tournament>/', TournamentView.as_view(), name='tournament'),
    path('tournaments/<slug:tournament>/<int:game>/', GameView.as_view(), name='game'),
]