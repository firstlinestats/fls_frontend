from django.shortcuts import render
from django.http import Http404
from playbyplay.models import Game, PlayByPlay
from team.models import Team
import datetime

# Create your views here.
def games(request):
    games = Game.objects.filter(dateTime__date__lte=datetime.date.today()).order_by('-dateTime', '-gamePk')[:100]
    teams = Team.objects.all().order_by('teamName')

    context = {
        'active_page': 'games',
        'game_list': games,
        'teams' : teams
    }

    return render(request, 'playbyplay/games.html', context)

def game_page(request, game_pk):
    try:
        game = Game.objects.get(gamePk = game_pk)
        pbp = PlayByPlay.objects.filter(gamePk=game_pk)

        #PN
        game.awayPN = 0
        game.homePN = 0
        for play in pbp:
            if play.team == game.homeTeam and play.playType == 'PENALTY':
                game.homePN += 1
            elif play.team == game.awayTeam and play.playType == 'PENALTY':
                game.awayPN += 1


        #Fenwick (FF)
        game.awayFF = int(game.awayShots) + int(game.awayMissed)
        game.homeFF = int(game.homeShots) + int(game.homeMissed)
        #MSF
        game.awayMSF = int(game.awayFF) - int(game.awayShots)
        game.homeMSF = int(game.homeFF) - int(game.homeShots)
        #Corsi
        game.awayCorsi = int(game.awayShots) + int(game.homeBlocked) + int(game.awayMissed)
        game.homeCorsi = int(game.homeShots) + int(game.awayBlocked) + int(game.homeMissed)
        #BSF
        game.awayBSF = int(game.homeBlocked)
        game.homeBSF = int(game.awayBlocked)
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
        game.awayHIT = int(game.awayHits)
        game.homeHIT = int(game.homeHits)
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


