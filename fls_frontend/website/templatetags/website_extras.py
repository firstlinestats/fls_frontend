from datetime import datetime

import pytz

from django import template

from playbyplay import models
from playbyplay.constants import gameStates

register = template.Library()

@register.filter()
def gameStatus(value):
    for state in gameStates:
        if state[0] == value:
            return state[1]
    return "Unknown"


@register.filter()
def checkOT(game):
    try:
        ot = models.GamePeriod.objects.get(game=game, period=4)
        return " (OT)"
    except:
        return ""
