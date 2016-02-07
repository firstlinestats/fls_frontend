import os
import sys
import json
import glob
import django

sys.path.append(os.path.join(os.path.dirname(__file__), "fls_frontend"))
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fls_frontend.settings")
from django.conf import settings

django.setup()

import api_calls

import team.models as tmodels
import player.models as pmodels
import playbyplay.models as pbpmodels


def main():
    #ingest_teams()
    #ingest_players()
    #ingest_games()
    ingest_pbp()


def ingest_pbp():
    for game in pbpmodels.Game.objects.all().order_by("gamePk"):
        if game.gameState not in ["1", "2", "8", "9"]:
            j = json.loads(api_calls.get_game(game.gamePk))
            print j.keys()
            # Update gameData
            gd = j["gameData"]
            game.dateTime = gd["datetime"]["dateTime"]
            game.endDateTime = gd["datetime"]["endDateTime"]
            game.gameState = gd["status"]["codedGameState"]
            # liveData
            ld = j["liveData"]
            # Get linescore information
            lineScore = ld["linescore"]
            game.homeScore = lineScore["teams"]["home"]["goals"]
            game.awayScore = lineScore["teams"]["away"]["goals"]
            game.homeShots = lineScore["teams"]["home"]["shotsOnGoal"]
            game.awayShot = lineScore["teams"]["away"]["shotsOnGoal"]
            # Get boxscore information
            # link

            # gamePk

            break


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
                    play.periodTime = get_period_time(entry["seconds"])
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
            player.currentTeam = tmodels.Team.objects.get(id=jinfo["currentTeam"]["id"])
        player.rosterStatus = jinfo["rosterStatus"]
        player.save()
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
