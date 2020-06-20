tournament = Tournament.objects.get(name=tournament)
players = Player.objects.filter(gameplayer_player__game__tournament=tournament).distinct().values_list('name', flat=True)
total_standings = {player: {'total': 0, 'wins': 0} for player in players}
games_standings = {}

for game in Game.objects.all():
    gameplayers = GamePlayer.objects.filter(game=game)
    game_standings = {gameplayer.player.name: {'score': 0, 'win': False} for gameplayer in gameplayers}
    for bet in Bet.objects.filter(round__game=game):
        score = 10 + bet.won*5 if bet.bet == bet.won else -abs(bet.bet-bet.won)*5
        game_standings[bet.player.name]['score'] += score
    for gameplayer in gameplayers:
        gameplayer.score = game_standings[gameplayer.player.name]['score']
        try:
            gameplayer.save()
        except Exception:
            pass


for game in Game.objects.all():
    rounds = Round.objects.filter(game=game)
    game_players = list(
        GamePlayer.objects.filter(game=game).order_by('id').values_list('player__name', flat=True))
    for i, rd in enumerate(rounds):
        pos = i % len(game_players)
        round_players = game_players[pos:] + game_players[:pos]
        bet = Bet.objects.get(round=rd, player__name=round_players[0])
        bet.hand = "hand"
        bet.save()
        bet = Bet.objects.get(round=rd, player__name=round_players[-1])
        bet.hand = "dessert"
        bet.save()