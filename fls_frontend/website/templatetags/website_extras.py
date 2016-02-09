from datetime import datetime

import pytz

from django import template

from playbyplay import models
from playbyplay.constants import gameStates, gameTypes

register = template.Library()


@register.filter()
def gameStatus(value):
    return check_constants(value, gameStates)


@register.filter()
def gameType(value):
    return check_constants(value, gameTypes)


@register.filter()
def checkOT(game):
    try:
        ot = models.GamePeriod.objects.get(game=game, period=4)
        return " (OT)"
    except:
        return ""


@register.filter()
def streakColor(streak):
    if "L" in streak:
        return "red"
    elif "W" in streak:
        return "green"
    elif "O" in streak:
        return "red"
    return "blue"


def check_constants(value, constant, unknown="Unknown"):
    for state in constant:
        if state[0] == value:
            return state[1]
    return unknown
