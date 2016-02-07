from django.shortcuts import render
from django.http import HttpResponse
from player.models import Player

# Create your views here.
def players(request):
    context = {
        'active_page' : 'players'
    }
    return render(request, 'player/players.html', context)