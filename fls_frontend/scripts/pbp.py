import os
import sys
import json
import glob
import time
import django

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


def check_game(gameid):
    j = json.loads(api_calls.get_game_timestamps(gameid))
    timestamps = j
    fp = open("../../../data/pbp/timestamps.json", "w")
    fp.write(str(timestamps))
    fp.close()


def get_timestamps(gameid):
    with open('../../../data/pbp/timestamps.json') as tstamps:
        data = json.load(tstamps)
    for x in xrange(1, len(data)):
        start = data[x-1]
        end = data[x]
        j = json.loads(api_calls.get_game_diff(gameid, start, end))
        fp = open("../../../data/pbp/game_" + str(gameid) + "_"
            + str(start) + "_" + str(end) + ".json", "w")
        fp.write(json.dumps(j, indent=4, sort_keys=True))
        fp.close()


def fix_gameId():
    shifts = set(pbpmodels.PlayByPlayPlayers.objects.values_list("play__gamePk__gamePk", flat=True).all())
    print len(shifts)
    allgames = pbpmodels.Game.objects.values_list("gamePk", flat=True).filter(gameState__in=[5, 6, 7])
    count = 0
    others = []
    for a in allgames:
        if a not in shifts:
            others.append(a)
    for dgame in reversed(others):
        count += 1
        print count, len(others)
        if count % 100 == 0:
            shifts = set(pbpmodels.PlayByPlayPlayers.objects.values_list("play__gamePk__gamePk", flat=True).all())
            print len(shifts)
        gameid = dgame
        test(gameid)
        break


@transaction.atomic()
def delete_duplicates():
    original = {}
    for shift in pbpmodels.PlayByPlayPlayers.objects.annotate(count=Count("play")).filter(count__gt=1):
        if shift.play.id not in original:
            original[shift.play.id] = shift
        else:
            shift.delete()


def test(gameid):
    allplayers = {}
    events = set()
    worthtimestamps = {}
    timestamps = json.loads(api_calls.get_game_timestamps(gameid))
    cont = True
    game = pbpmodels.Game.objects.values("dateTime", "endDateTime").get(gamePk=gameid)
    startDateTime = datetime.strftime(game["dateTime"], "%Y%m%d_%H%M%S")
    endDateTime = datetime.strftime(game["endDateTime"], "%Y%m%d_%H%M%S")
    eventIds = pbpmodels.PlayByPlay.objects.values_list("eventId", flat=True).filter(gamePk_id=gameid)
    for x in xrange(1, len(timestamps)):
        start = timestamps[x-1]
        end = timestamps[x]
        if start <= startDateTime and end <= endDateTime:
            print "huzzah"
            j = api_calls.get_game_diff(gameid, start, end)
            if "eventId" in j:
                j = json.loads(j)
                for diff in j:
                    if "diff" in diff:
                        paths = diff["diff"]
                        for path in paths:
                            if "eventId" in path["path"] and "eventIdx" not in path["path"]:
                                if path["value"] in eventIds:
                                    worthtimestamps[path["value"]] = end
    worhttimestamps = worthtimestamps.values()
    """for pbp in pbpmodels.PlayByPlay.objects.filter(gamePk_id=gameid):
        if pbpmodels.PlayByPlayPlayers.objects.filter(play=pbp).exists():
            print "already exists..."
            cont = False
            break
        dateTime = pbp.dateTime
        sdateTime = datetime.strftime(dateTime, "%Y%m%d_%H%M%S")
        found = False
        for ts in xrange(1, len(timestamps)):
            start = timestamps[ts-1]
            end = timestamps[ts]
            print start, sdateTime, end
            if start < sdateTime and end > sdateTime:
                worthtimestamps.append(start)
                found = True
                break
            elif start == sdateTime:
                worthtimestamps.append(start)
                found = True
                break
            elif end == sdateTime:
                worthtimestamps.append(end)
                found = True
                break"""
    byevents = {}
    #jsonload = None
    #print len(worthtimestamps), len(timestamps)
    if cont is True:
        print len(worthtimestamps)
        for ts in worthtimestamps:
            #forstart = datetime.now()
            j = json.loads(api_calls.get_game_at(gameid, ts))
            #forjsonload = datetime.now() - forstart
            #if jsonload is None:
            #    jsonload = forjsonload
            #else:
            #    jsonload += forjsonload
            if "currentPlay" in j["liveData"]["plays"]:
                awayplayers = j["liveData"]["boxscore"]['teams']['away']['onIce']
                homeplayers = j["liveData"]["boxscore"]['teams']['home']['onIce']
                eventId = j["liveData"]["plays"]["currentPlay"]["about"]["eventId"]
                results = {"away": awayplayers, "home": homeplayers,
                    "homeScore": j["liveData"]["plays"]["currentPlay"]["about"]["goals"]["home"],
                    "awayScore": j["liveData"]["plays"]["currentPlay"]["about"]["goals"]["away"],
                    "eventIdx": j["liveData"]["plays"]["currentPlay"]["about"]["eventIdx"]
                }
                if len(homeplayers) > 0 and len(awayplayers) > 0:
                    byevents[eventId] = results
        getPbp = None
        for eventId in byevents:
            try:
                #forstart = datetime.now()
                pbp = pbpmodels.PlayByPlay.objects.get(gamePk_id=gameid,
                    eventId=eventId)
                pbp.homeScore = byevents[eventId]["homeScore"]
                pbp.awayScore = byevents[eventId]["awayScore"]
                #pbp.eventId = eventId
                #pbp.eventIdx = byevents[eventId]["eventIdx"]
                pbp.save()
                pbpid = pbp.id
                #forgetpbp = datetime.now() - forstart
                #if getPbp is None:
                #    getPbp = forgetpbp
                #else:
                #    getPbp += forgetpbp
                players = {}
                for h in xrange(len(homeplayers)):
                    players["h" + str(h + 1) + "_id"] = homeplayers[h]
                for a in xrange(len(awayplayers)):
                    players["a" + str(a + 1) + "_id"] = awayplayers[a]
                players["play_id"] = pbpid
                pbpp = pbpmodels.PlayByPlayPlayers(**players)
                allplayers[eventId] = pbpp
            except Exception as e:
                print gameid, eventId, e
        #create = datetime.now()
        print len(allplayers.values())
        pbpmodels.PlayByPlayPlayers.objects.bulk_create(allplayers.values())


def pbp(gameid):
    with open('../../../data/pbp/timestamps.json') as tstamps:
        timestamps = set([str(x) for x in json.load(tstamps)])
    for pbp in pbpmodels.PlayByPlay.objects.filter(gamePk_id=gameid).order_by("dateTime"):
        dt = pbp.dateTime.strftime("%Y%m%d_%H%M%S")
        #if dt not in timestamps:
            
        


def main():
    #check_game(2015020756)
    #get_timestamps(2015020756)
    #test(2015020756)
    #pbp(2015020756)
    fix_gameId()
    #delete_duplicates()


if __name__ == "__main__":
    main()
