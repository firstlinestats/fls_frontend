from django.shortcuts import render
from playbyplay.models import Game

# Create your views here.
def games(request):
    context = {'active_page' : 'games'}
    return render(request, 'playbyplay/games.html', context)