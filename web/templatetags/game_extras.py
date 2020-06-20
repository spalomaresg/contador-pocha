from django import template
import math
from itertools import cycle

register = template.Library()


@register.filter(name='get_num_cards')
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


@register.filter
def get_diff(bet, won):
    return abs(bet - won)


@register.filter(name='get')
def get(elem, key):
    return elem.get(key, "")


@register.filter(name='get_bets')
def get_bets(bets):
    bets_count = 0
    wons_count = 0
    for bet in bets:
        bets_count += bet['bet']
        wons_count += bet['won']

    return bets_count
    # return "{}/{}".format(bets_count, wons_count)


@register.filter(name='is_bigger')
def is_bigger(n1, n2):
    return float(n1) >= float(n2)
