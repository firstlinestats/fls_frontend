from datetime import datetime

import pytz

from django import template

from playbyplay import models
from playbyplay.constants import gameStates, gameTypes

from player.constants import playerPositions

register = template.Library()


@register.filter()
def get_cpm(player):
    return player["cf"] - player["ca"]


@register.filter()
def get_fpm(player):
    return player["ff"] - player["fa"]


@register.filter
def getkey(player, key):
    return player[key]


@register.filter()
def birth(player):
    birthplace = ""
    if len(player.birthCity) > 0:
        birthplace = player.birthCity
    if len(player.birthStateProvince) > 0:
        if len(birthplace) > 0:
            birthplace += ", " + player.birthStateProvince
        else:
            birthplace = player.birthStateProvince
    if len(player.birthCountry) > 0:
        if len(birthplace) > 0:
            birthplace += ", " + player.birthCountry
        else:
            birthplace = player.birthCountry
    return birthplace


@register.filter()
def handedness(value):
    if value == "R":
        return "Right"
    elif value == "L":
        return "Left"
    return value


@register.filter()
def fixHeight(value):
    if len(value) == 5:
        return value[0:3] + "0" + value[3:]
    return value


@register.filter()
def position(value):
    for position in playerPositions:
        if position[0] == value:
            return position[1]
    return value


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
