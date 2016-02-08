from django.shortcuts import render
from playbyplay.models import Game
from team.models import Venue
from team.models import Team
import datetime

# Create your views here.
def games(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:50]
    teams = Team.objects.all().order_by('teamName')

    context = {
        'active_page': 'games',
        'game_list': games,
        'teams' : teams
    }

    return render(request, 'playbyplay/games.html', context)
