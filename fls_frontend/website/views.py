from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from playbyplay.models import Game
from team.models import Team
import datetime
# Create your views here.

def index(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:15]
    teams = Team.objects.all()
    context = {
        'game_list': games,
        'teams': teams
    }
    return render(request, 'website/index.html', context)