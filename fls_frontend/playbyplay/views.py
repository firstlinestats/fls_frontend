from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core import serializers

from .forms import GamesFilter
from playbyplay.models import Game, PlayByPlay, PlayerGameStats, GoalieGameStats
from team.models import Team
import datetime

# Create your views here.
def games(request):
    if request.method == 'POST':
        print request.POST
        
        games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:100]
        
        data = serializers.serialize('json', games)
        return HttpResponse(data, content_type='application/json')

    else:
        games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:100]
        form = GamesFilter()
        context = {
            'active_page': 'games',
            'game_list': games,
            'form' : form
        }

        return render(request, 'playbyplay/games.html', context)




def game_page(request, game_pk):
    try:
        game = Game.objects.get(gamePk = game_pk)
        if game.gameState in ['3', '4', '5', '6', '7']:
            pbp = PlayByPlay.objects.filter(gamePk=game_pk)
            playerStats = PlayerGameStats.objects.filter(game=game_pk).order_by('team', 'player__lastName')
            goalieStats = GoalieGameStats.objects.filter(game=game_pk)


            #Goalie Stats
            game.goalieStats = goalieStats

            #Player Stats
            game.homePlayers = []
            game.awayPlayers = []
            for player in playerStats:
                player.points = player.goals + player.assists
                player.faceOffLost = player.faceoffTaken - player.faceOffWins
                if player.team == game.homeTeam:
                    game.homePlayers.append(player)
                elif player.team == game.awayTeam:
                    game.awayPlayers.append(player)


            #PN
            game.awayPN = 0
            game.homePN = 0
            for play in pbp:
                if play.team == game.homeTeam and play.playType == 'PENALTY':
                    game.homePN += 1
                elif play.team == game.awayTeam and play.playType == 'PENALTY':
                    game.awayPN += 1


            #Fenwick (FF)
            game.awayFF = game.awayShots + game.awayMissed
            game.homeFF = game.homeShots + game.homeMissed
            #MSF
            game.awayMSF = game.awayFF - game.awayShots
            game.homeMSF = game.homeFF - game.homeShots
            #Corsi
            game.awayCorsi = game.awayShots + game.homeBlocked + game.awayMissed
            game.homeCorsi = game.homeShots + game.awayBlocked + game.homeMissed
            #BSF
            game.awayBSF = game.homeBlocked
            game.homeBSF = game.awayBlocked
            #SCF
            game.awaySCF = None
            game.homeSCF = None
            #HSCF
            game.awayHSCF = None
            game.homeHSCF = None
            #ZSO
            game.awayZSO = None
            game.homeZSO = None
            #HIT
            game.awayHIT = game.awayHits
            game.homeHIT = game.homeHits
            #FO_W
            game.awayFO_W = None
            game.homeFO_W = None
            #TOI
            game.awayTOI = None
            game.homeTOI = None   
    except Game.DoesNotExist:
        raise Http404("Game does not exist!")
    return render(request, 'playbyplay/game_page.html', {
        'game': game
    })


