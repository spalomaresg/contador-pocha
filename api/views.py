from django.shortcuts import render
from rest_framework.decorators import api_view

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from api.models import *
from api.serializers import *

import json
import math
from collections import deque


@csrf_exempt
def tournament_list(request):
    if request.method == 'GET':
        snippets = Tournament.objects.all()
        serializer = TournamentSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TournamentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def tournament_games(request, tournament):
    if request.method == 'GET':
        snippets = Game.objects.filter(tournament__name=tournament)
        serializer = GameSerializerGet(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        data['tournament'] = Tournament.objects.get(name=tournament).id
        players = data.pop('players')
        serializer = GameSerializer(data=data)
        if serializer.is_valid():
            game = serializer.save()
            for player in players:
                player, created = Player.objects.get_or_create(name=player)
                GamePlayer(game=game, player=player).save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def tournament_next_players(request, tournament):
    response = {'next_players': []}
    tournament = Tournament.objects.get(name=tournament)
    last_game = Game.objects.filter(tournament=tournament).order_by('id').last()
    if last_game:
        next_players = deque(GamePlayer.objects.filter(game=last_game).order_by('id').values_list('player__name', flat=True))
        next_players.rotate(-1)
        response['next_players'] = list(next_players)
    return JsonResponse(response)


@csrf_exempt
def tournament_standings(request, tournament):
    tournament = Tournament.objects.get(name=tournament)
    players = Player.objects.filter(gameplayer_player__game__tournament=tournament).distinct().values_list('name', flat=True)
    total_standings = {player: {'total': 0, 'wins': 0} for player in players}
    games_standings = {}
    for game in Game.objects.filter(tournament=tournament).order_by('date'):
        players_pos = game.get_game_players_pos()
        games_standings[game.date.strftime("%d-%m-%Y")] = {player: players_pos.get(player, {}) for player in players}
        for player, details in players_pos.items():
            total_standings[player]['total'] += details['score']
            if details['pos'] == 'victory':
                total_standings[player]['wins'] += 1

    return JsonResponse({
        'total_standings': {k: v for k, v in sorted(total_standings.items(), key=lambda item: item[1]['total'], reverse=True)},
        'games_standings': games_standings
    })


def tournament_stats(request, tournament):
    """
    lose streak

    """
    tournament = Tournament.objects.get(name=tournament)
    players = list(Player.objects.filter(gameplayer_player__game__tournament=tournament).distinct().values_list('name', flat=True))
    game_max_players = max([len(GamePlayer.objects.filter(game=game)) for game in Game.objects.filter(tournament=tournament)])
    max_cards = math.floor(40/game_max_players) if players else 0
    stats = {
        'players': players,
        'game_max_players': [i for i in range(1, game_max_players + 1)],
        'by_hand_pos': {i: {'win': 0, 'total': 0} for i in range(0, max_cards)},
        'by_hand_pos_player': {player: {i: {'win': 0, 'total': 0} for i in range(0, max_cards)} for player in players},
        'by_lose_type': {player: {'under': 0, 'total': 0} for player in players},
        'total_bets': {player: 0 for player in players},
        'total_wins_zero': {player: 0 for player in players},
        'total_loses_zero': {player: 0 for player in players},
        'players_bets': {player: {i: {'win': 0, 'lose': 0, 'total': 0} for i in range(0, max_cards+1)} for player in players},
        'players_game_phases': {player: {'ascending': 0,
                                         'max_cards': 0,
                                         'descending': 0,
                                         'total_games': 0} for player in players + ['Promedio']},
        'players_game_pos': {player: {'victory': {'score': 0, 'total': 0},
                                      'podium': {'score': 0, 'total': 0},
                                      'other': {'score': 0, 'total': 0},
                                      'defeat': {'score': 0, 'total': 0}} for player in players + ['Promedio']},
        'player_rounds_pos': {player: {i: {'score': 0, 'total': 0} for i in range(1, game_max_players+1)} for player in
                         players},
    }
    games = Game.objects.filter(tournament__name=tournament)
    for game in games:
        game_players = list(GamePlayer.objects.filter(game=game).order_by('id').values_list('player__name', flat=True))
        game_players_pos = game.get_game_players_pos()
        # max_cards = len(game_players_pos)
        for player, details in game_players_pos.items():
            stats['players_game_phases'][player]['total_games'] += 1
            stats['players_game_phases']['Promedio']['total_games'] += 1
            stats['players_game_pos'][player][details['pos']]['score'] += details['score']
            stats['players_game_pos'][player][details['pos']]['total'] += 1
            stats['players_game_pos']['Promedio'][details['pos']]['score'] += details['score']
            stats['players_game_pos']['Promedio'][details['pos']]['total'] += 1
        rounds = Round.objects.filter(game=game)
        game_phase = 'ascending'
        max_cards = math.floor(40/len(game_players))
        for num_round, rd in enumerate(rounds):
            pos = num_round % len(game_players)
            round_players = game_players[pos:] + game_players[:pos]
            if rd.num_cards == max_cards and rounds[num_round-1].num_cards < max_cards:
                game_phase = "max_cards"
            elif num_round and rounds[num_round-1].num_cards > rd.num_cards:
                game_phase = "descending"
            for i, player in enumerate(round_players):
                bet = Bet.objects.get(round=rd, player__name=player)
                win = bet.bet == bet.won
                score = 10 + bet.won * 5 if bet.bet == bet.won else -abs(bet.bet - bet.won) * 5
                stats['by_hand_pos'][i]['total'] += 1
                stats['by_hand_pos_player'][player][i]['total'] += 1
                stats['players_bets'][player][bet.bet]['total'] += 1
                stats['total_bets'][player] += bet.bet
                stats['players_game_phases'][player][game_phase] += score
                stats['players_game_phases']['Promedio'][game_phase] += score
                stats['player_rounds_pos'][player][i+1]['score'] += score
                stats['player_rounds_pos'][player][i+1]['total'] += 1
                if win:
                    stats['by_hand_pos'][i]['win'] += 1
                    stats['by_hand_pos_player'][player][i]['win'] += 1
                    stats['players_bets'][player][bet.bet]['win'] += 1
                    if bet.bet == 0:
                        stats['total_wins_zero'][player] += 1
                else:
                    stats['by_lose_type'][player]['total'] += 1
                    stats['by_lose_type'][player]['under'] += 1 if bet.bet < bet.won else 0
                    stats['players_bets'][player][bet.bet]['lose'] += 1
                    if bet.bet == 0:
                        stats['total_loses_zero'][player] += 1
    """for hand_pos, details in stats['by_hand_pos'].items():
        stats['by_hand_pos'][hand_pos] = details['win'] / details['total']
    for player, hands_pos in stats['by_hand_pos_player'].items():
        for hand_pos, details in hands_pos.items():
            stats['by_hand_pos_player'][player][hand_pos] = details['win'] / details['total']"""
    for player, details in stats['by_lose_type'].items():
        if details['total']:
            stats['by_lose_type'][player] = details['under'] / details['total']
    for player, details in stats['players_game_phases'].items():
        player_details = stats['players_game_phases'][player]
        if stats['players_game_phases'][player]['total_games']:
            player_details['ascending'] = "{:0.2f}".format(player_details['ascending'] /
                                                           stats['players_game_phases'][player]['total_games'])
            player_details['max_cards'] = "{:0.2f}".format(player_details['max_cards'] /
                                                           stats['players_game_phases'][player]['total_games'])
            player_details['descending'] = "{:0.2f}".format(player_details['descending'] /
                                                            stats['players_game_phases'][player]['total_games'])
    for player, pos_details in stats['players_game_pos'].items():
        for pos, details in pos_details.items():
            if details['total']:
                details['score'] = "{:0.2f}".format(details['score'] / details['total'])
    for player, pos_details in stats['player_rounds_pos'].items():
        for pos, details in pos_details.items():
            if details['total']:
                details['score'] = "{:0.2f}".format(details['score'] / details['total'])

    return JsonResponse(stats)


def game_info_old(request, tournament, game):
    if request.method != 'GET':
        return JsonResponse({})

    return JsonResponse({
        'id': game,
        'tournament': tournament,
        'date': Game.objects.get(id=game).date,
        'players': list(Player.objects.filter(gameplayer_player__game=game).values_list('name', flat=True)),
        'rounds': [{'num_cards': round.num_cards, 'bets': [{'bet': bet.bet, 'won': bet.won} for bet in Bet.objects.filter(round=round)]} for round in Round.objects.filter(game=game)]
    })


def game_info(request, tournament, game):
    if request.method == 'GET':
        game = Game.objects.get(id=game)
        serializer = GameSerializerGet(game)
        data = serializer.data
        players_pos = {player['player']: i for i, player in enumerate(data['players'])}
        for _round in data['rounds']:
            _round['bets'] = sorted(_round['bets'], key=lambda bet: players_pos[bet['player']])
        next_round_players = list(GamePlayer.objects.filter(game=game).order_by('id').values_list('player__name', flat=True))
        pos = len(data['rounds']) % len(data['players'])
        next_round_players = next_round_players[pos:] + next_round_players[:pos]
        data['numCards'] = get_num_cards(data)
        data['next_round_players'] = next_round_players
        return JsonResponse(data, safe=False)


def get_num_cards(game):
    rounds = game.get('rounds', [])
    num_players = len(game.get('players', []))
    rounds_num_cards = [round['num_cards'] for round in rounds]
    if not rounds:
        return 1
    else:
        max_cards = math.floor(40 / len(game['players']))
        prev_num_cards = rounds_num_cards[-1]
        if game['repeat_one'] and (len(rounds_num_cards) < num_players or rounds_num_cards[-1] == 2):
            return 1
        elif game['repeat_highest'] and len(rounds_num_cards) >= max_cards and rounds_num_cards[-num_players] != max_cards and rounds_num_cards[-1] in [max_cards, max_cards-1]:
            return max_cards
        elif len(rounds_num_cards) > 1 and prev_num_cards == 1 and not game['repeat_one']:
            return 0
        else:
            if max_cards in rounds_num_cards:
                return prev_num_cards - 1
            else:
                return prev_num_cards + 1


def game_last_round(request, tournament, game):
    rounds = list(Round.objects.filter(game__id=game))
    last_round = rounds[-1].id if rounds else 0
    return JsonResponse({
        'last_round': last_round
    })


def player_list(request):
    if request.method == 'GET':
        snippets = Player.objects.all()
        serializer = PlayerSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PlayerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def round_list(request):
    if request.method == 'POST':
        print(request.POST)
        data = JSONParser().parse(request)
        serializer = RoundSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
