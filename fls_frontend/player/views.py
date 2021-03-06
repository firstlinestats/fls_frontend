from __future__ import division
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q

from player.forms import PlayerStatsFilter
from player.models import Player

from playbyplay.models import Game, PlayerGameStats
from playbyplay.constants import gameTypes

import helpers

import datetime


# Create your views here.
def player(request, player_id):
    context = {
        'active_page': 'players'
    }
    context['player'] = get_object_or_404(Player, id=player_id)
    
    return render(request, 'player/player.html', context)


def skaters(request):
    context = {
        'active_page' : 'players'
    }
    context["form"] = PlayerStatsFilter()
    return render(request, 'player/skaters.html', context)


def skatersTable(request):
    if request.method == 'GET':
        currentSeason = Game.objects.latest("endDateTime").season
        getValues = dict(request.GET)
        args = ()
        kwargs = {
            'game__gameState__in': [6, 7, 8],
            'game__season__in': [currentSeason, ]
        }
        if "date_start" in getValues and "date_end" in getValues:
            try:
                date_start = datetime.datetime.strptime(getValues["date_start"][0], "%m/%d/%Y").date()
                date_end =  datetime.datetime.strptime(getValues["date_end"][0], "%m/%d/%Y").date()

                kwargs['game__dateTime__gte'] = date_start
                kwargs['game__dateTime__lte'] = date_end
            except:
                date_start = None
                date_end = None
        bySeason = False
        if "divide_by_season" in getValues:
            if "on" == getValues["divide_by_season"][0]:
                bySeason = True
        game_types = gameTypes
        if "game_type" in getValues and len(getValues["game_type"]) > 0:
            game_types = getValues["game_type"]
            kwargs['game__gameType__in'] = game_types
        venues = None
        if "venues" in getValues and len(getValues["venues"]) > 0:
            venues = getValues["venues"]
            kwargs['game__venue__name__in'] = venues
        teams = None
        if "teams" in getValues and len(getValues["teams"]) > 0:
            teams = getValues["teams"]
            args = ( Q(game__awayTeam__in = getValues['teams']) | Q(game__homeTeam__in = getValues['teams']), )
        toi = None
        if "toi" in getValues and len(getValues["toi"]) > 0:
            try:
                toi = int(getValues["toi"][0])
                if toi > 60:
                    h, m = divmod(toi, 60)
                    kwargs['timeOnIce__gte'] = "%02d:%02d:00" % (h, m)
                else:
                    kwargs['timeOnIce__gte'] = "00:%02d:00" % (toi, )
            except:
                pass
        seasons = currentSeason
        if "seasons" in getValues and len(getValues["seasons"]) > 0:
            seasons = getValues["seasons"]
            kwargs['game__season__in'] = seasons
        home_or_away = None
        if "home_or_away" in getValues and len(getValues["home_or_away"]) > 0:
            try:
                home_or_away = int(getValues["home_or_away"][0])
                if home_or_away == 1:
                    home_or_away = False
                elif home_or_away == 2:
                    home_or_away = True
                else:
                    home_or_away = None
            except:
                pass
        positions = None
        if "position" in getValues and len(getValues["position"]) > 0:
            positions = getValues["position"]
            kwargs['player__primaryPositionCode__in'] = positions



        context = {}
        today = datetime.date.today()
        start = datetime.datetime.now()
        tgameStats = PlayerGameStats.objects\
            .values("player__fullName", "player__currentTeam__shortName",
                "player__currentTeam", "player__primaryPositionCode",
                "player__birthDate", "player__weight", "player__height",
                "player__currentTeam__abbreviation", "hits",
                "player__id", "timeOnIce", "assists", "goals", "shots",
                "powerPlayGoals", "powerPlayAssists", "penaltyMinutes",
                "faceOffWins", "faceoffTaken", "takeaways", "giveaways",
                "shortHandedGoals", "shortHandedAssists", "blocked",
                "plusMinus", "evenTimeOnIce", "powerPlayTimeOnIce",
                "shortHandedTimeOnIce", "player__id", "team",
                "game__homeTeam", "game__season")\
            .filter(*args, **kwargs).iterator()
        if bySeason is False:
            gameStats = {}
        else:
            seasonStats = {}
        pid = "player__id"
        exclude = set([pid, "player__birthDate", "player__primaryPositionCode",
            "player__fullName", "player__currentTeam", "team",
            "player__currentTeam__abbreviation", "player__id",
            "player__currentTeam__shortName", "player__height", "player__weight"])
        for t in tgameStats:
            counts = True
            if home_or_away is not None:
                counts = False
                if home_or_away is True and t["team"] == t["game__homeTeam"]:
                    counts = True
                elif home_or_away is False and t["team"] != t["game__homeTeam"]:
                    counts = True
            if counts is True:
                if bySeason is True:
                    if t["game__season"] not in seasonStats:
                        seasonStats[t["game__season"]] = {}
                    gameStats = seasonStats[t["game__season"]]
                if t[pid] not in gameStats:
                    gameStats[t[pid]] = t
                    gameStats[t[pid]]["games"] = 0
                    gameStats[t[pid]]["age"] = helpers.calculate_age(t["player__birthDate"], today=today)
                else:
                    gameStats[t[pid]]["games"] += 1
                    for key in t:
                        if key not in exclude:
                            if isinstance(gameStats[t[pid]][key], datetime.time):
                                gameStats[t[pid]][key] = helpers.combine_time(gameStats[t[pid]][key], t[key])
                            elif isinstance(gameStats[t[pid]][key], datetime.timedelta):
                                gameStats[t[pid]][key] += datetime.timedelta(minutes=t[key].minute, seconds=t[key].second)
                            else:
                                if gameStats[t[pid]][key] is not None:
                                    gameStats[t[pid]][key] += t[key]
                                else:
                                    gameStats[t[pid]][key] = t[key]
        if bySeason is True:
            gameStats = {}
            for key in seasonStats:
                for pid in seasonStats[key]:
                    gameStats[str(key)+"|"+str(pid)] = seasonStats[key][pid]
        print datetime.datetime.now() - start
        for t in gameStats:
            games = gameStats[t]["games"]
            if games != 0:
                gameStats[t]["G60"] = round(gameStats[t]["goals"] / gameStats[t]["timeOnIce"].total_seconds() * 60 * 60, 2)
                gameStats[t]["A60"] = round(gameStats[t]["assists"] / gameStats[t]["timeOnIce"].total_seconds() * 60 * 60, 2)
                gameStats[t]["P60"] = gameStats[t]["G60"] + gameStats[t]["A60"]
                m, s = divmod(round(gameStats[t]["timeOnIce"].total_seconds() / games, 2), 60)
                gameStats[t]["TOIGm"] = "%02d:%02d" % (m, s)
                if gameStats[t]["faceoffTaken"] > 0:
                    gameStats[t]["facPercent"] = round((float(gameStats[t]["faceOffWins"]) / float(gameStats[t]["faceoffTaken"])) * 100, 2)
                else:
                    gameStats[t]["facPercent"] = 0
            else:
                gameStats[t]["G60"] = 0
                gameStats[t]["A60"] = 0
                gameStats[t]["P60"] = 0
                gameStats[t]["TOIGm"] = 0
                gameStats[t]["facPercent"] = 0
        context["gameStats"] = gameStats
        return render(request, "player/skatersTable.html", context)
