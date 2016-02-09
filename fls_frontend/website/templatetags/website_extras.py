from datetime import datetime

import pytz

from django import template

from playbyplay.constants import gameStates

register = template.Library()

@register.filter()
def gameStatus(value):
    for state in gameStates:
        if state[0] == value:
            return state[1]
    return "Unknown"


@register.filter()
def convertDate(value):
    if value is not None:
        localtimezone = pytz.timezone('US/Eastern')
        return value.astimezone(localtimezone)
    return ""
