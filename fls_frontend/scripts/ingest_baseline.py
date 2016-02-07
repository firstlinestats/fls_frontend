import os
import sys
import json
import glob
import django

sys.path.append(os.path.join(os.path.dirname(__file__), "fls_frontend"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fls_frontend.settings")
from django.conf import settings
from django.db import transaction

django.setup()

import api_calls

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels
import playbyplay.helper as pbphelper


def main():
    #ingest_teams()
    #ingest_players()
    #ingest_games()
    ingest_pbp()


@transaction.atomic
def ingest_pbp():
    allshootouts = []
    allperiods = []
    allplaybyplay = []
    allplayers = []
    players = {}
    playid = 0
    tplayers = pmodels.Player.objects.all()
    for t in tplayers:
        players[t.id] = t
    tallpbps = pbpmodels.PlayByPlay.objects.all()
    allpbps = {}
    for t in tallpbps:
        allpbps[str(t.gamePk_id) + "|" + str(t.eventId)] = t
    tallpois = pbpmodels.PlayerOnIce.objects.all()
    allpois = {}
    for t in tallpois:
        allpois[str(t.play.id) + "|" + str(t.game.gamePk) + "|" + str(t.player.id)] = t
    for game in pbpmodels.Game.objects.all().order_by("gamePk"):
        if game.gameState not in ["1", "2", "8", "9"]:
            print game.gamePk
            j = json.loads(api_calls.get_game(game.gamePk))
            homeSkaters = j["liveData"]["boxscore"]["teams"]["home"]["skaters"]
            homeGoalies = j["liveData"]["boxscore"]["teams"]["home"]["goalies"]
            homeOnIce = j["liveData"]["boxscore"]["teams"]["home"]["onIce"]
            homeScratches = j["liveData"]["boxscore"]["teams"]["home"]["scratches"]
            awaySkaters = j["liveData"]["boxscore"]["teams"]["away"]["skaters"]
            awayGoalies = j["liveData"]["boxscore"]["teams"]["away"]["goalies"]
            awayOnIce = j["liveData"]["boxscore"]["teams"]["away"]["onIce"]
            awayScratches = j["liveData"]["boxscore"]["teams"]["away"]["scratches"]
            homeIds = set(homeSkaters + homeGoalies + homeOnIce + homeScratches)
            awayIds = set(awaySkaters + awayGoalies + awayOnIce + awayScratches)
            gd = j["gameData"]
            # Player Info
            pinfo = gd["players"]
            for sid in pinfo: # I swear that's not a Crosby reference
                iid = int(sid.replace("ID", ""))
                if iid not in players:
                    if iid in homeIds:
                        team = game.homeTeam
                    elif iid in awayIds:
                        team = game.awayTeam
                    else:
                        print iid, homeIds, awayIds
                        raise Exception
                    player = ingest_player(pinfo[sid], team.id)
                    players[player.id] = player
            # liveData
            ld = j["liveData"]
            lineScore = ld["linescore"]
            # Plays
            for play in ld["plays"]["allPlays"]:
                about = play["about"]
                pplayers = play["players"]
                result = play["result"]
                coordinates = play["coordinates"]
                #if str(game.gamePk) + "|" + str(about["eventIdx"]) in allpbps:
                #    p = allpbps[str(game.gamePk_id) + "|" + str(about["eventIdx"])]
                #else:
                p = pbpmodels.PlayByPlay()
                p.pkey = playid
                p.gamePk = game
                p.eventId = about["eventIdx"]
                p.period = about["period"]
                p.periodTime = about["periodTime"]
                p.dateTime = about["dateTime"]
                p.playType = result["eventTypeId"]
                p.playDescription = result["description"]
                if "secondaryType" in result:
                    if p.playType == "PENALTY":
                        p.penaltyType = result["secondaryType"]
                    else:
                        p.shotType = result["secondaryType"]
                if p.playType == "PENALTY":
                    p.penaltySeverity = result["penaltySeverity"]
                    p.penaltyMinutes = result["penaltyMinutes"]
                if "strength" in result:
                    p.strength = result["strength"]["code"]
                if "x" in coordinates:
                    p.xcoord = coordinates["x"]
                    p.ycoord = coordinates["y"]
                p.homeScore = lineScore["teams"]["home"]["goals"]
                p.awayScore = lineScore["teams"]["away"]["goals"]
                allplaybyplay.append(p)
                #p.save()
                #allpbps[str(p.gamePk_id) + "|" + str(p.eventId)] = p
                for pp in pplayers:
                    #if str(p.id) + "|" + str(game.gamePk) + "|" + str(pp["player"]["id"]) in allpois:
                    #    poi = allpois[str(p.id) + "|" + str(game.gamePk) + "|" + str(pp["player"]["id"])]
                    #else:
                    poi = pbpmodels.PlayerOnIce()
                    poi.play_id = playid
                    poi.game = game
                    poi.player_id = pp["player"]["id"]
                    poi.player_type = pbphelper.get_player_type(pp["playerType"])
                    allplayers.append(poi)
                    #poi.save()
                    #allpois[str(p.id) + "|" + str(game.gamePk) + "|" + str(pp["player"]["id"])] = poi
                playid += 1
            # Update gameData
            game.dateTime = gd["datetime"]["dateTime"]
            game.endDateTime = gd["datetime"]["endDateTime"]
            game.gameState = gd["status"]["codedGameState"]
            # Get linescore information
            game.homeScore = lineScore["teams"]["home"]["goals"]
            game.awayScore = lineScore["teams"]["away"]["goals"]
            game.homeShots = lineScore["teams"]["home"]["shotsOnGoal"]
            game.awayShot = lineScore["teams"]["away"]["shotsOnGoal"]
            # Get period specific information
            cperiod = 1
            for period in lineScore["periods"]:
                #try:
                #    p = pbpmodels.GamePeriod.objects.get(game=game, period=period["num"])
                #except:
                p = pbpmodels.GamePeriod()
                p.game = game
                p.period = period["num"]
                if period["num"] > cperiod:
                    cperiod = period["num"]
                p.startTime = period["startTime"]
                p.endTime = period["endTime"]
                p.homeScore = period["home"]["goals"]
                p.homeShots = period["home"]["shotsOnGoal"]
                p.awayScore = period["away"]["goals"]
                p.awayShots = period["away"]["shotsOnGoal"]
                allperiods.append(p)
                #p.save()
            if lineScore["hasShootout"]:
                sinfo = lineScore["shootoutInfo"]
                try:
                    s = pbpmodels.Shootout.objects.get(game=game)
                except:
                    s = pbpmodels.Shootout()
                    s.game = game
                s.awayScores = sinfo["away"]["scores"]
                s.awayAttempts = sinfo["away"]["attempts"]
                s.homeScores = sinfo["home"]["scores"]
                s.homeAttempts = sinfo["home"]["attempts"]
                allshootouts.append(s)
                #s.save()
            # Get boxscore information
            boxScore = ld["boxscore"]
            home = boxScore["teams"]["home"]["teamStats"]["teamSkaterStats"]
            away = boxScore["teams"]["away"]["teamStats"]["teamSkaterStats"]
            game.homePIM = home["pim"]
            game.awayPIM = away["pim"]
            game.homePPGoals = home["powerPlayGoals"]
            game.awayPPGoals = away["powerPlayGoals"]
            game.homePPOpportunities = home["powerPlayOpportunities"]
            game.awayPPOpportunities = away["powerPlayOpportunities"]
            game.homeFaceoffPercentage = home["faceOffWinPercentage"]
            game.awayFaceoffPercentage = away["faceOffWinPercentage"]
            game.homeBlocked = home["blocked"]
            game.awayBlocked = away["blocked"]
            game.homeTakeaways = home["takeaways"]
            game.awayTakeaways = away["takeaways"]
            game.homeGiveaways = home["giveaways"]
            game.awayGiveaways = away["giveaways"]
            game.homeHits = home["hits"]
            game.awayHits = away["hits"]
            game.save()
            hp = boxScore["teams"]["home"]["players"]
            ap = boxScore["teams"]["away"]["players"]
            set_player_stats(hp, game.homeTeam, game, players, cperiod)
            set_player_stats(ap, game.awayTeam, game, players, cperiod)
        pbpmodels.Shootout.objects.bulk_create(allshootouts)
        pbpmodels.GamePeriod.objects.bulk_create(allperiods)
        pbpmodels.PlayByPlay.objects.bulk_create(allplaybyplay)
        pbpmodels.PlayerOnIce.objects.bulk_create(allplayers)
        

def set_player_stats(pd, team, game, players, period):
    pgss = []
    for sid in pd: # I swear that's not a Crosby reference
        iid = int(sid.replace("ID", ""))
        if "skaterStats" in pd[sid]["stats"]:
            jp = pd[sid]["stats"]["skaterStats"]
            if iid not in players:
                player = ingest_player(jp)
                players[player.id] = player
            else:
                player = players[iid]
            #try:
            #    pgs = pbpmodels.PlayerGameStats.objects.get(player=player, game=game)
            #except:
            pgs = pbpmodels.PlayerGameStats()
            pgs.player = player
            pgs.game = game
            pgs.timeOnIce = "00:" + jp["timeOnIce"]
            pgs.assists = jp["assists"]
            pgs.goals = jp["goals"]
            pgs.shots = jp["shots"]
            pgs.hits = jp["hits"]
            pgs.powerPlayGoals = jp["powerPlayGoals"]
            pgs.powerPlayAssists = jp["powerPlayAssists"]
            pgs.penaltyMinutes = jp["penaltyMinutes"]
            pgs.faceOffWins = jp["faceOffWins"]
            pgs.faceoffTaken = jp["faceoffTaken"]
            pgs.takeaways = jp["takeaways"]
            pgs.giveaways = jp["giveaways"]
            pgs.shortHandedGoals = jp["shortHandedGoals"]
            pgs.shortHandedAssists = jp["shortHandedAssists"]
            pgs.blocked = jp["blocked"]
            pgs.plusMinus = jp["plusMinus"]
            pgs.evenTimeOnIce = "00:" + jp["evenTimeOnIce"]
            pgs.powerPlayTimeOnIce = "00:" + jp["powerPlayTimeOnIce"]
            pgs.shortHandedTimeOnIce = "00:" + jp["shortHandedTimeOnIce"]
            pgs.period = period
            pgss.append(pgs)
    pbpmodels.PlayerGameStats.objects.bulk_create(pgss)


def get_shifts(gid):
    # Get timecodes
    # For the diff between timecode and timecode after it
    #   Look for paths that start with /liveData/boxscore/teams/{{ home/away }}/onIce/
    #   Record those changes based on time from previously found
    pass


def get_woi_players():
    tplayers = pmodels.Player.objects.all()
    players = {}
    for t in tplayers:
        players[str(t.fullName)] = t.id
    convert = {}
    first = True
    for line in open("../../../data/roster.unique.csv"):
        if first is False:
            line = line.split(",")
            name = line[5].replace("\"", "").strip()
            woiid = line[8].replace("\"", "").strip()
            if name in players:
                convert[str(woiid)] = players[name]
            else:
                print name
        else:
            first = False
    return convert



def ingest_pbp_old():
    woi = get_woi_players()
    playtypes = set()
    playtext = set()
    types = set()
    types2 = set()
    games = pbpmodels.Game.objects.all().order_by("gamePk")
    count = 0
    play_convert = {"TAKE": "TAKEAWAY",
        "SOC": "SHOOTOUT_COMPLETE",
        "HIT": "HIT", "ICING": "STOP", "GIVE": "GIVEAWAY",
        "MISS": "MISSED_SHOT", "STOP": "STOP", "PEND": "PENALTY_END",
        "BLOCK": "BLOCKED_SHOT", "FAC": "FACEOFF", "PENL": "PENALTY",
        "SHOT": "SHOT", "OFFSIDE": "STOP"}
    playcount = 0
    for game in games:
        count += 1
        print count, len(games)
        existing = pbpmodels.PlayByPlay.objects.values("gamePk").filter(gamePk=game.gamePk)
        jpbp = None
        if len(existing) == 0:
            gcode = int(str(game.gamePk)[5:])
            files = glob.glob("../../../data/games" + str(game.season) + "*.json")
            for fp in files:
                begend = fp.replace("../../../data/games" + str(game.season) + "_", "").replace(".json", "").split("_")
                begend = [int(x) for x in begend]
                if gcode >= begend[0] and gcode <= begend[1]:
                    fp = open(fp)
                    j = json.load(fp)
                    for jg in j:
                        first = jg[0]
                        if int(first["season"]) == game.season and int(first["gcode"]) == gcode:
                            jpbp = jg
                            break
                    fp.close()
                    if jpbp is not None:
                        break
            if jpbp is not None:
                plays = []
                pois = []
                missing = 0
                for entry in jpbp:
                    play = pbpmodels.PlayByPlay()
                    play.id = playcount
                    playcount += 1
                    play.gamePk_id = game.gamePk
                    play.gameState = 3
                    play.period = entry["period"]
                    play.periodTime = "00:" + get_period_time(entry["seconds"])
                    play.homeScore = entry["home.score"]
                    play.awayScore = entry["away.score"]
                    if entry["etype"] in play_convert:
                        play.playType = play_convert[entry["etype"]]
                        play.playDescription = entry["etext"]
                        if play.playType == "SHOT":
                            play.shotType = entry["type"]
                            if entry["etext"] is not None and entry["type2"] is not None:
                                play.playDescription = entry["etext"] + " | " + entry["type2"]
                            elif entry["etext"] is not None:
                                play.playDescription = entry["etext"]
                            elif entry["type2"] is not None:
                                play.playDescription = entry["type2"]
                        elif play.playType == "PENALTY":
                            play.penaltySeverity = entry["type"]
                            play.penaltyMinutes = int(entry["type"][entry["type"].find("(")+1:entry["type"].find(")")].replace(" min", "").replace(" maj", "").replace("maj", "5"))
                    play.xcoord = entry["xcoord"]
                    play.ycoord = entry["ycoord"]
                    play.timeOnIce = entry["event.length"]
                    plays.append(play)
                    for ap in ["a1", "a2", "a3", "a4", "a5", "a6",
                                "h1", "h2", "h3", "h4", "h5", "h6"]:
                        poi = getPOI(playcount, game, entry, ap, woi)
                        if poi is not None:
                            pois.append(poi)
                        else:
                            missing += 1
                print len(pois), missing
                #pbpmodels.PlayByPlay.objects.bulk_create(plays)
                #pbpmodels.PlayerOnIce.objects.bulk_create(pois)


def getPOI(playcount, game, play, ap, woi):
    if play[ap] is not None:
        poi = pbpmodels.PlayerOnIce()
        poi.play_id = playcount
        poi.game = game
        if str(play[ap]) in woi:
            poi.player_id = woi[play[ap]]
        else:
            return None
        if play["etype"] == "FAC":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 1
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 2
        elif play["etype"] == "HIT":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 3
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 4
        elif play["etype"] == "SHOT":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
        elif play["etype"] == "BLOCK":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 9
        elif play["etype"] == "MISS":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 7
        elif play["etype"] == "GOAL":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 5
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 6
            elif play["ev.player.3"] == play[ap]:
                poi.player_type = 16
        elif play["etype"] == "PENL":
            if play["ev.player.1"] == play[ap]:
                poi.player_type = 10
            elif play["ev.player.2"] == play[ap]:
                poi.player_type = 11
        if poi.player_type is None:
            poi.player_type = 15
        return poi


    return None



def get_period_time(seconds):
    ps = 0
    period = "1st"
    if seconds <= 1200:
        ps = seconds
        period = "1st"
    elif seconds > 1200 and seconds <= 2400:
        ps = seconds - 1200
        period = "2nd"
    elif seconds > 2400 and seconds <= 3600:
        ps = seconds - 2400
        period = "3rd"
    else:
        ps = seconds - 3600
        period = "OT"
    minutes, seconds = divmod(ps, 60)
    seconds = str(seconds)
    minutes = str(minutes)
    if len(seconds) == 1:
        seconds = "0" + seconds
    if len(minutes) == 1:
        minutes = "0" + minutes
    return str(minutes) + ":" + str(seconds)

                


def ingest_games():
    season = 20152016
    tgames = set(pbpmodels.Game.objects.values_list("gamePk", flat=True).all())
    for team in tmodels.Team.objects.all():
        tid = team.id
        egames = get_games(tid, str(season), egames=tgames)


def get_games(tid, season, egames=set()):
    result = json.loads(api_calls.get_schedule(tid, season))
    games = []
    if "dates" in result:
        for jgames in result["dates"]:
            for jgame in jgames["games"]:
                if jgame["gamePk"] not in egames:
                    egames.add(jgame["gamePk"])
                    game = pbpmodels.Game()
                    game.gamePk = jgame["gamePk"]
                    game.link = jgame["link"]
                    game.gameType = jgame["gameType"]
                    game.season = jgame["season"]
                    game.dateTime = jgame["gameDate"]
                    game.awayTeam_id = jgame["teams"]["away"]["team"]["id"]
                    game.homeTeam_id = jgame["teams"]["home"]["team"]["id"]
                    try:
                        game.venue = tmodels.Venue.objects.get(name=jgame["venue"]["name"])
                    except:
                        venue = tmodels.Venue()
                        venue.name = jgame["venue"]["name"]
                        venue.save()
                        game.venue = venue
                    game.homeScore = jgame["teams"]["home"]["score"]
                    game.awayScore = jgame["teams"]["away"]["score"]
                    game.gameState = jgame["status"]["statusCode"]
                    games.append(game)
    pbpmodels.Game.objects.bulk_create(games)
    return egames



def ingest_players():
    # For each team, get the roster
    team_rosters = {}
    for team in tmodels.Team.objects.all():
        team_rosters[team.id] = set()
        api = json.loads(api_calls.get_team_roster(team.id))
        for player in api["roster"]:
            team_rosters[team.id].add(player["person"]["id"])
    for team in team_rosters:
        jplayers = json.loads(api_calls.get_player(ids=team_rosters[team]))["people"]
        for jinfo in jplayers:
            ingest_player(jinfo, team)


def ingest_player(jinfo, team=None):
    try:
        player = pmodels.Player()
        player.id = jinfo["id"]
        player.fullName = jinfo["fullName"]
        player.link = jinfo["link"]
        player.firstName = jinfo["firstName"]
        player.lastName = jinfo["lastName"]
        if "primaryNumber" in jinfo:
            player.primaryNumber = jinfo["primaryNumber"]
        player.primaryPositionCode = jinfo["primaryPosition"]["code"]
        player.birthDate = jinfo["birthDate"]
        player.birthCity = jinfo["birthCity"]
        player.birthCountry = jinfo["birthCountry"]
        player.height = jinfo["height"]
        player.weight = jinfo["weight"]
        player.active = jinfo["active"]
        player.rookie = jinfo["rookie"]
        if "shootsCatches" in jinfo:
            player.shootsCatches = jinfo["shootsCatches"]
        if team is not None:
            player.currentTeam_id = team
        else:
            print jinfo
            player.currentTeam = tmodels.Team.objects.get(id=jinfo["currentTeam"]["id"])
        player.rosterStatus = jinfo["rosterStatus"]
        player.save()
        return player
    except Exception as e:
        print jinfo["id"], e
        


def ingest_teams():
    teams = api_calls.get_teams()
    teams = json.loads(teams)
    for jteam in teams["teams"]:
        team = tmodels.Team()
        team.id = jteam["id"]
        team.name = jteam["name"]
        team.shortName = jteam["shortName"]
        team.link = jteam["link"]
        team.abbreviation = jteam["abbreviation"]
        team.teamName = jteam["teamName"]
        team.locationName = jteam["locationName"]
        team.firstYearOfPlay = jteam["firstYearOfPlay"]
        team.conference = jteam["conference"]["name"][0]
        team.division = jteam["division"]["name"][0]
        team.officialSiteUrl = jteam["officialSiteUrl"]
        team.active = jteam["active"]

        venue = tmodels.Venue()
        venue.name = jteam["venue"]["name"]
        venue.city = jteam["venue"]["city"]
        venue.timeZone = jteam["venue"]["timeZone"]["id"]
        venue.timeZoneOffset = jteam["venue"]["timeZone"]["offset"]
        venue.save()

        team.venue = venue
        team.save()


if __name__ == "__main__":
    main()
