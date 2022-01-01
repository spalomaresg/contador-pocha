from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from datetime import date


class Tournament(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    tournament = models.ForeignKey(Tournament, related_name="games", on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    repeat_one = models.BooleanField(default=False)
    repeat_highest = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        unique_together = ['id', 'tournament']

    def __str__(self):
        return "{} - {}".format(self.tournament, self.date)

    def get_game_players_pos(self):
        game_players = GamePlayer.objects.filter(game=self)
        scores = sorted(list(set(game_players.values_list('score', flat=True))), reverse=True)
        players_pos = {}
        for game_player in game_players:
            score = game_player.score
            if score == scores[0]:
                players_pos[game_player.player.name] = {'pos': 'victory', 'score': score}
            elif score in scores[:3]:
                players_pos[game_player.player.name] = {'pos': 'podium', 'score': score}
            elif score == scores[-1]:
                players_pos[game_player.player.name] = {'pos': 'defeat', 'score': score}
            else:
                players_pos[game_player.player.name] = {'pos': 'other', 'score': score}
        if players_pos['Mama']['pos'] == 'victory':
            print(self)
        return players_pos


class Player(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class GamePlayer(models.Model):
    RESULT_CHOICES = (
        ("victory","victory"),
        ("podium","podium"),
        ("defeat","defeat"),
        ("other","other")
    )
    game = models.ForeignKey(Game, related_name="gameplayers", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="gameplayer_player", on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0)
    result = models.CharField(max_length=7,choices = RESULT_CHOICES,default="other",blank=True)

    class Meta:
        ordering = ['-score', 'id']
        unique_together = ['game', 'player']

    def __str__(self):
        return "{} - {} - {}".format(self.game.tournament, self.game.date, self.player.name)


class Round(models.Model):
    game = models.ForeignKey(Game, related_name="rounds", on_delete=models.CASCADE)
    num_cards = models.PositiveSmallIntegerField()


class Bet(models.Model):
    HAND_CHOICES = (
        ("", ""),
        ("hand", "hand"),
        ("dessert", "dessert"),
    )

    PHASE_CHOICES = (
        ("ascending","ascending"),
        ("max_cards","max_cards"),
        ("descending", "descending")
    )
    round = models.ForeignKey(Round, related_name="bets", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="bet_player", on_delete=models.CASCADE)
    bet = models.PositiveSmallIntegerField()
    won = models.PositiveSmallIntegerField()
    score = models.SmallIntegerField(default=0)
    hand = models.CharField(max_length=10, choices=HAND_CHOICES, default="", blank=True)
    phase = models.CharField(max_length=11,choices = PHASE_CHOICES,default="ascending",blank=True)
    position = models.PositiveSmallIntegerField(default="0")


@receiver(post_save, sender=Bet)
def bet_save(sender, instance, created, **kwargs):
    gameplayer = GamePlayer.objects.get(game=instance.round.game, player__name=instance.player)
    if created:
        round_score = 10 + instance.won*5 if instance.bet == instance.won else -abs(instance.bet-instance.won)*5
        gameplayer.score += round_score
        gameplayer.save()
    else:
        score = 0
        for bet in Bet.objects.filter(round__game=instance.round.game, player=gameplayer.player):
            round_score = 10 + bet.won * 5 if bet.bet == bet.won else -abs(bet.bet - bet.won) * 5
            score += round_score
        gameplayer.score = score
        try:
            gameplayer.save()
        except Exception:
            pass


@receiver(post_delete, sender=Bet)
def bet_delete(sender, instance, **kwargs):
    try:
        gameplayer = GamePlayer.objects.get(game=instance.round.game, player__name=instance.player)
        round_score = 10 + instance.won * 5 if instance.bet == instance.won else -abs(instance.bet - instance.won) * 5
        gameplayer.score -= round_score
        gameplayer.save()
    except Exception:
        pass
