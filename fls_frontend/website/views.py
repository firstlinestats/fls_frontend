from django.shortcuts import render
from django.http import HttpResponse
from playbyplay.models import Game
from team.models import Team
import datetime
# Create your views here.

def index(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:30]
    teams = Team.objects.all()
    context = {
        'active_page': 'index',
        'game_list': games,
        'teams': teams
    }
    return render(request, 'website/index.html', context)

def about(request):
    context = {
        'active_page': 'about'
    }
    return render(request, 'website/about.html', context)