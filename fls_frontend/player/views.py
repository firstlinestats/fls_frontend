from __future__ import division
from django.shortcuts import render
from django.http import HttpResponse
from player.models import Player
from playbyplay.models import Game, PlayerGameStats

import helpers

import datetime

# Create your views here.
def players(request):
    context = {
        'active_page' : 'players'
    }
    players = Player.objects.all()
    currentSeason = Game.objects.latest("endDateTime").season
    tgameStats = PlayerGameStats.objects\
        .values("player__fullName", "player__currentTeam__shortName",
            "player__currentTeam", "player__primaryPositionCode",
            "player__birthDate",
            "player__currentTeam__abbreviation", "hits",
            "player__id", "timeOnIce", "assists", "goals", "shots",
            "powerPlayGoals", "powerPlayAssists", "penaltyMinutes",
            "faceOffWins", "faceoffTaken", "takeaways", "giveaways",
            "shortHandedGoals", "shortHandedAssists", "blocked",
            "plusMinus", "evenTimeOnIce", "powerPlayTimeOnIce",
            "shortHandedTimeOnIce")\
        .filter(game__season=currentSeason)
    gameStats = {}
    pid = "player__id"
    exclude = [pid, "player__birthDate", "player__primaryPositionCode",
        "player__fullName", "player__currentTeam",
        "player__currentTeam__abbreviation",
        "player__currentTeam__shortName"]
    for t in tgameStats:
        if t[pid] not in gameStats:
            gameStats[t[pid]] = t
            gameStats[t[pid]]["games"] = 0
            gameStats[t[pid]]["age"] = helpers.calculate_age(t["player__birthDate"])
        else:
            gameStats[t[pid]]["games"] += 1
            for key in t:
                if key not in exclude:
                    if isinstance(gameStats[t[pid]][key], datetime.time):
                        gameStats[t[pid]][key] = helpers.combine_time(gameStats[t[pid]][key], t[key])
                    elif isinstance(gameStats[t[pid]][key], datetime.timedelta):
                        gameStats[t[pid]][key] += datetime.timedelta(minutes=t[key].minute, seconds=t[key].second)
                    else:
                        gameStats[t[pid]][key] += t[key]
    for t in gameStats:
        games = gameStats[t]["games"]
        if games != 0:
            gameStats[t]["G60"] = round(gameStats[t]["goals"] / gameStats[t]["timeOnIce"].total_seconds() * 60 * 60, 2)
            gameStats[t]["A60"] = round(gameStats[t]["assists"] / gameStats[t]["timeOnIce"].total_seconds() * 60 * 60, 2)
            gameStats[t]["P60"] = gameStats[t]["G60"] + gameStats[t]["A60"]
            m, s = divmod(round(gameStats[t]["timeOnIce"].total_seconds() / games, 2), 60)
            gameStats[t]["TOIGm"] = "%02d:%02d" % (m, s)
        else:
            gameStats[t]["G60"] = 0
            gameStats[t]["A60"] = 0
            gameStats[t]["P60"] = 0
            gameStats[t]["TOIGm"] = 0
    context["gameStats"] = gameStats
    return render(request, 'player/players.html', context)