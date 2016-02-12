from django.shortcuts import render
from django.http import HttpResponse
from playbyplay.models import Game
from team.models import Team, SeasonStats
import datetime
import json
# Create your views here.

def index(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:30]
    #teams = Team.objects.all()
    teamdata = {}
    currentSeason = games[0].season
    max_date = SeasonStats.objects.latest("date")
    standings = SeasonStats.objects.filter(date=max_date.date).order_by("-points")
    teamdata = sorted(teamdata.items(), key=lambda k: k[1]["p"])
    context = {
        'active_page': 'index',
        'game_list': games,
        'teams': standings
    }
    historical = SeasonStats.objects.values("team__teamName",
        "points", "date", "team__division").filter(season=max_date.season).order_by("date")
    hstand = {}
    for h in historical:
        sdate = str(h["date"])
        teamName = h["team__teamName"]
        division = h["team__division"]
        points = h["points"]
        if division not in hstand:
            hstand[division] = {}
        if teamName not in hstand[division]:
            hstand[division][teamName] = []
        hstand[division][teamName].append({"date": sdate, "points": points})

    context["divisions"] = json.dumps(hstand, ensure_ascii=True)
    return render(request, 'website/index.html', context)

def about(request):
    context = {
        'active_page': 'about'
    }
    return render(request, 'website/about.html', context)