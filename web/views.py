from django.shortcuts import render
from django.views.generic import TemplateView

import requests
from django.urls import reverse


class TournamentsView(TemplateView):
    template_name = "web/tournaments.html"

    def get(self, request, *args, **kwargs):
        context = {
            'tournaments': requests.get("http://127.0.0.1:8000/api/tournaments/").json()
        }

        return render(request, self.template_name, context)


class TournamentView(TemplateView):
    template_name = "web/tournament.html"

    def get(self, request, *args, **kwargs):
        tournament = self.kwargs['tournament']
        games = requests.get("http://127.0.0.1:8000/api/tournaments/{}/games/".format(tournament)).json()
        context = {
            'tournament': tournament,
            'games': games,
            'players': requests.get("http://127.0.0.1:8000/api/players/").json(),
            'next_players': requests.get("http://127.0.0.1:8000/api/tournaments/{}/next_players/".format(tournament)).json(),
            'standings': requests.get("http://127.0.0.1:8000/api/tournaments/{}/standings/".format(tournament)).json(),
            'stats': requests.get("http://127.0.0.1:8000/api/tournaments/{}/stats/".format(tournament)).json()
        }

        return render(request, self.template_name, context)


class GameView(TemplateView):
    template_name = "web/game.html"

    def get(self, request, *args, **kwargs):
        tournament = self.kwargs['tournament']
        game = self.kwargs['game']
        game = requests.get("http://127.0.0.1:8000/api/tournaments/{}/{}/".format(tournament, game)).json()
        last_round = game['rounds'][-1]['id'] if game['rounds'] else 0
        context = {
            'game': game,
            'last_round': last_round
        }

        return render(request, self.template_name, context)
