from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from asgiref.sync import sync_to_async
import httpx
import asyncio
from django.utils.decorators import classonlymethod

import requests
from django.urls import reverse


# These 3 views implementations aim to serve as a testing environment
# for the async view compatibility. 

# For that reason one will find both class and function-based views. 
# The usage of native async-compatible http libraries, in this case
# "xhttp", works perfectly but when trying to use non-compatible async
# libraries like "requests" things get messed up. In order to run "requests"
# synchronous code within an async view the usage of asgiref.sync wrapper
# functions is necessary. Actually it is the documented prefered method
# but for some reason it doesn work.

async def tournaments(request):
    async with httpx.AsyncClient() as client:
        r = await client.get("http://127.0.0.1:8000/api/tournaments/")
        context = {
            'tournaments': r.json()
        }
        return render(request, "web/tournaments.html", context)

async def tournament(request,tournament):

    print(tournament)
    async with httpx.AsyncClient(timeout=10.0) as client:
        games = await client.get("http://127.0.0.1:8000/api/tournaments/{}/games/".format(tournament))
        players = await client.get("http://127.0.0.1:8000/api/players/".format(tournament))
        next_players = await client.get("http://127.0.0.1:8000/api/tournaments/{}/next_players/".format(tournament))
        standings = await client.get("http://127.0.0.1:8000/api/tournaments/{}/standings/".format(tournament))
        stats = await client.get("http://127.0.0.1:8000/api/tournaments/{}/stats/".format(tournament))
    
    context = {
        'tournament': tournament,
        'games': games.json(),
        'players': players.json(),
        'next_players': next_players.json(),
        'standings': standings.json(),
        'stats': stats.json(),
    }

    return render(request, "web/tournament.html", context)


# In order to make this view async one has to mark it as 
# a co-routine. Documentation suggests preprending "async def"
# to the view's __call__() method but it doesn't seem to work.
# Alternatively one can overwrite the as_view() method as shown
# below

class GameView(TemplateView):
    template_name = "web/game.html"

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request, *args, **kwargs):
        tournament = self.kwargs['tournament']
        game = self.kwargs['game']
        async with httpx.AsyncClient(timeout=10.0) as client:
            game = await client.get("http://127.0.0.1:8000/api/tournaments/{}/{}/".format(tournament, game))
            game = game.json()
            last_round = game['rounds'][-1]['id'] if game['rounds'] else 0
            context = {
                'game': game,
                'last_round': last_round
            }

            return render(request, self.template_name, context)
