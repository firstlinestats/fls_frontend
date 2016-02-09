from django.shortcuts import render
from django.http import HttpResponse
from playbyplay.models import Game
from team.models import Team, SeasonStats
import datetime
# Create your views here.

def index(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:30]
    #teams = Team.objects.all()
    teamdata = {}
    currentSeason = games[0].season
    standings = SeasonStats.objects.filter(season=currentSeason).order_by("-points")
    teamdata = sorted(teamdata.items(), key=lambda k: k[1]["p"])
    context = {
        'active_page': 'index',
        'game_list': games,
        'teams': standings
    }
    return render(request, 'website/index.html', context)

def about(request):
    context = {
        'active_page': 'about'
    }
    return render(request, 'website/about.html', context)