from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q

from .forms import GamesFilter, GameStatsFilter
from playbyplay.models import Game, PlayByPlay, PlayerGameStats, GoalieGameStats
from team.models import Team
import datetime

# Create your views here.

def game_list(request):    
    form = GamesFilter()
    return render(request, 'playbyplay/game_list.html', {
        'active_page': 'games',
        'form' : form
    })


def game_list_table(request):
    if request.method == 'GET':
        currentSeason = Game.objects.latest("endDateTime").season
        getValues = dict(request.GET)

        kwargs = {
            'gameState__in' : [6,7,8],
            'season' : currentSeason
        }
        args = ()
        
        if 'teams' in getValues:
            args = ( Q(awayTeam__in = getValues['teams']) | Q(homeTeam__in = getValues['teams']), )
        if 'seasons' in getValues:
            kwargs['season__in'] = getValues['seasons']
        if 'venues' in getValues:
            if getValues['venues'][0]:
                kwargs['venue__name'] = getValues['venues'][0]
        if 'gameType' in getValues:
            kwargs['gameType__in'] = getValues['gameType']
        if "date_start" in getValues and "date_end" in getValues:
            try:
                date_start = datetime.datetime.strptime(getValues["date_start"][0], "%m/%d/%Y").date()
                date_end =  datetime.datetime.strptime(getValues["date_end"][0], "%m/%d/%Y").date()

                kwargs['dateTime__gte'] = date_start
                kwargs['dateTime__lte'] = date_end
            except:
                date_start = None
                date_end = None  
  

        games = Game.objects\
            .values('dateTime', 'gameType', 'awayTeam', 'homeTeam', 'awayTeam__abbreviation', 
                'homeTeam__abbreviation', 'homeTeam__id', 
                'awayTeam__id', 'homeScore', 'awayScore', 'awayShots', 
                'homeShots', 'awayBlocked', 'homeBlocked', 'awayMissed',
                'homeMissed', 'gameState', 'endDateTime', 'gamePk')\
            .filter(*args, **kwargs).order_by('-gamePk')
        return render(request, 'playbyplay/game_list_table.html', {'game_list' : games })



def game_page(request, game_pk):
    game = Game.objects.get(gamePk = game_pk)
    form = GameStatsFilter()
    return render(request, 'playbyplay/game_page.html', {
        'game': game,
        'form': form
    })

def game_tables(request):
    try:
        gamePk = dict(request.GET)['game_pk'][0]
        game = Game.objects.get(gamePk = gamePk)
        if game.gameState in ['3', '4', '5', '6', '7']:
            pbp = PlayByPlay.objects.filter(gamePk=gamePk)
            playerStats = PlayerGameStats.objects.filter(game=gamePk).order_by('team', 'player__lastName')
            goalieStats = GoalieGameStats.objects.filter(game=gamePk)


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
    return render(request, 'playbyplay/game_tables.html', {
        'game': game
    })




