import os
import sys
import json
import glob
import time
import django

from bs4 import BeautifulSoup

from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "fls_frontend"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fls_frontend.settings")
from django.conf import settings

django.setup()

import api_calls

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels
import playbyplay.helper as pbphelper
from django.db import transaction
from django.db.models import Count
from django.db.utils import IntegrityError

LIVE_BASE = "http://live.nhl.com/GameData/"  # Base URL for the live data reports

BASE = "http://www.nhl.com/scores/htmlreports/"  # Base URL for html reports


def try_live():
    for game in pbpmodels.Game.objects.filter(gameState__in=[5, 6, 7]):
        pbps = pbpmodels.PlayByPlay.objects.filter(gamePk=game)
        eventIds = {}
        for pbp in pbps:
            if pbp.eventId not in eventIds:
                eventIds[pbp.eventId] = pbp
        url = LIVE_BASE + str(game.season) + "/" + str(game.gamePk) + "/PlayByPlay.json"
        j = json.loads(api_calls.get_url(url))
        count = set()
        if "data" in j:
            data = j["data"]
            if "game" in data:
                jgame = data["game"]
                if "plays" in jgame:
                    for play in jgame["plays"]["play"]:
                        if play["eventid"] in eventIds:
                            pbp = eventIds[play["eventid"]]
                            count.add(play["eventid"])
        missing = set()
        for ei in eventIds:
            if ei not in count:
                missing.add(eventIds[ei].playType)
        print missing
        break


def get_old():
    for game in pbpmodels.Game.objects.filter(gameState__in=[5, 6, 7]):
        eventIdxs = {}
        pbps = pbpmodels.PlayByPlay.objects.values("eventIdx", "id").filter(gamePk=game)
        for pbp in pbps:
            if pbp["eventIdx"] not in eventIdxs:
                eventIdxs[pbp["eventIdx"]] = pbp["id"]
        print game.gamePk
        if not pbpmodels.PlayerOnIce.objects.filter(play_id__in=eventIdxs.values()).exists():
            playerstats = pbpmodels.PlayerGameStats.objects.values("team_id", "player__fullName", "player_id").filter(game=game)
            hp = {}
            ap = {}
            for ps in playerstats:
                if ps["team_id"] == game.homeTeam_id:
                    hp[ps["player__fullName"].upper()] = ps["player_id"]
                else:
                    ap[ps["player__fullName"].upper()] = ps["player_id"]
            goaliestats = pbpmodels.GoalieGameStats.objects.values("team_id", "player__fullName", "player_id").filter(game=game)
            for gs in goaliestats:
                if gs["team_id"] == game.homeTeam_id:
                    hp[gs["player__fullName"].upper()] = gs["player_id"]
                else:
                    ap[gs["player__fullName"].upper()] = gs["player_id"]
            url = BASE + str(game.season) + "/PL0" + str(game.gamePk)[5:] + ".HTM"
            data = api_calls.get_url(url)
            soup = BeautifulSoup(data, 'html.parser')
            #table = soup.find('table', attrs={'id': 'GameInfo'})
            evens = soup.find_all('tr', attrs={'class': 'evenColor'})
            count = 0
            saved = []
            with transaction.atomic():
                for row in evens:
                    cols = row.find_all('td', recursive=False)
                    fonts = row.find_all('font')
                    fcols = [ele.text.strip().replace("\n", "") for ele in cols]
                    eventIdx = int(fcols[0])
                    if eventIdx in eventIdxs:
                        players = fcols[6:]
                        away = players[0]
                        home = players[1]
                        away = [x[0:-1] for x in away.replace(u'\xa0', " ").split(" ")]
                        home = [x[0:-1] for x in home.replace(u'\xa0', " ").split(" ")]
                        awayNames = {}
                        homeNames = {}
                        for f in fonts:
                            title = f["title"].split(" - ")[-1]
                            number = f.text
                            if number in away and number not in awayNames:
                                awayNames[number] = title
                            else:
                                homeNames[number] = title
                        acount = 1
                        players = set()
                        for anum in away:
                            if len(anum) > 0:
                                pbpdict = {}
                                pbpdict["play_id"] = eventIdxs[eventIdx]
                                pbpdict["game_id"] = game.gamePk
                                anum = int(anum)
                                player = getPlayer(ap, awayNames, anum) #ap[awayNames[str(anum)]]
                                if player not in players:
                                    players.add(player)
                                    pbpdict["player_id"] = player
                                    acount += 1
                                    try:
                                        pbpp = pbpmodels.PlayerOnIce(**pbpdict)
                                        #pbpp.save()
                                        saved.append(pbpp)
                                    except TypeError:
                                        pass
                        hcount = 1
                        for hnum in home:
                            if len(hnum) > 0:
                                pbpdict = {}
                                pbpdict["play_id"] = eventIdxs[eventIdx]
                                pbpdict["game_id"] = game.gamePk
                                hnum = int(hnum)
                                player = getPlayer(hp, homeNames, hnum)
                                if player not in players:
                                    players.add(player)
                                    pbpdict["player_id"] = player
                                    hcount += 1
                                    try:
                                        pbpp = pbpmodels.PlayerOnIce(**pbpdict)
                                        #pbpp.save()
                                        saved.append(pbpp)
                                    except TypeError:
                                        pass
                pbpmodels.PlayerOnIce.objects.bulk_create(saved)


def getPlayer(playerDict, number2name, currnum):
    currnum = str(currnum)
    if number2name[currnum] in playerDict:
        return playerDict[number2name[currnum]]
    sn = number2name[currnum].split(" ")
    # check for first name?
    for name in playerDict:
        ps = name.split(" ")
        if len(ps) == len(sn):
            fp = ps[0]
            sp = sn[0]
            if fp in sp or sp in fp and ps[1] == sn[1]:
                return playerDict[name]
    # check for last name? seriously NHL?
    for name in playerDict:
        ps = name.split(" ")
        if len(ps) == len(sn):
            fp = ps[-1]
            sp = sn[-1]
            if fp == sp:
                return playerDict[name]
    # check for player who didn't even play in that game, really NHL???
    try:
        player = pmodels.Player.objects.get(fullName__iexact=number2name[currnum])
        return player.id
    except Exception as e:
        print e
    print number2name[currnum], currnum, playerDict
    raise Exception


def change_model():
    count = 0
    length = pbpmodels.Game.objects.filter(gameState__in=[5, 6, 7]).count()
    for game in pbpmodels.Game.objects.filter(gameState__in=[5, 6, 7]):
        count += 1
        if count % 100 == 0:
            print count, length
        if not pbpmodels.PlayerOnIce.objects.filter(game=game).exists():
            with transaction.atomic():
                for play in pbpmodels.PlayByPlayPlayers.objects.filter(play__gamePk__gamePk=game.gamePk)\
                        .values("play__gamePk_id", "play_id", "a1_id", "a2_id", "a3_id",
                            "a4_id", "a5_id", "a6_id", "a7_id", "h1_id", "h2_id", "h3_id",
                            "h4_id", "h5_id", "h6_id", "h7_id"):
                    game_id = play["play__gamePk_id"]
                    play_id = play["play_id"]
                    teams = ["a", "h"]
                    for team in teams:
                        for x in xrange(1, 8):
                            player_id = play[team + str(x) + "_id"]
                            if player_id is not None:
                                data = {"player_id": player_id,
                                    "play_id": play_id,
                                    "game_id": game_id}
                                try:
                                    poi = pbpmodels.PlayerOnIce(**data)
                                    poi.save()
                                except IntegrityError:
                                    pass


if __name__ == "__main__":
    get_old()
