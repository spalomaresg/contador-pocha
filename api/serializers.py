from rest_framework import serializers
from api.models import *


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name']


class GamePlayerSerializer(serializers.ModelSerializer):
    player = serializers.StringRelatedField(many=False)

    class Meta:
        model = GamePlayer
        fields = ['game', 'player']


class BetSerializer(serializers.ModelSerializer):
    player = serializers.StringRelatedField(many=False)

    class Meta:
        model = Bet
        fields = ['id', 'player', 'bet', 'won', 'hand']


class RoundSerializer(serializers.ModelSerializer):
    bets = BetSerializer(many=True)

    class Meta:
        model = Round
        fields = ['id', 'game', 'num_cards', 'bets']

    def validate_bets(self, bets):
        for i, bet in enumerate(self.initial_data.get('bets')):
            bets[i]['player'] = Player.objects.get(name=bet['player'])
        return bets

    def create(self, validated_data):
        bets_data = validated_data.pop('bets')
        round = Round.objects.create(**validated_data)
        for bet_data in bets_data:
            Bet.objects.create(round=round, **bet_data)
        return round


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name']


class GamePlayerSerializer(serializers.ModelSerializer):
    player = serializers.StringRelatedField(many=False)

    class Meta:
        model = GamePlayer
        fields = ['game', 'player']


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['id', 'date', 'tournament', 'repeat_one', 'repeat_highest']


class GameSerializerGet(serializers.ModelSerializer):
    tournament = serializers.StringRelatedField(many=False, read_only=True)
    rounds = RoundSerializer(many=True, read_only=True)
    players = GamePlayerSerializer(many=True, read_only=True, source="gameplayers")

    class Meta:
        model = Game
        fields = ['id', 'tournament', 'date', 'rounds', 'players', 'repeat_one', 'repeat_highest']
