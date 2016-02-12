import os
import sys
import json
import glob
import django

from datetime import datetime, timedelta, date

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


@transaction.atomic
def findStandings(season, tdate):
    j = json.loads(api_calls.get_standings(tdate))
    for record in j["records"]:
        division = record["division"]["name"][0]
        conference = record["division"]["name"][0]
        for team in record["teamRecords"]:
            stat = tmodels.SeasonStats()
            stat.team_id = team["team"]["id"]
            stat.season = season
            try:
                stat.goalsAgainst = team["goalsAgainst"]
                stat.goalsScored = team["goalsScored"]
            except:
                pass
            stat.points = team["points"]
            stat.gamesPlayed = team["gamesPlayed"]
            stat.wins = team["leagueRecord"]["wins"]
            stat.losses = team["leagueRecord"]["losses"]
            stat.ot = team["leagueRecord"]["ot"]
            stat.date = tdate
            try:
                stat.streakCode = team["streak"]["streakCode"]
            except:
                pass
            stat.save()


@transaction.atomic
def ingest_standings():
    start_date = date(2016, 2, 9)
    end_date = date(2016, 2, 10)
    for single_date in daterange(start_date, end_date):
        print single_date
        tdate = single_date.strftime("%Y-%m-%d")
        findStandings(20152016, tdate)



def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == "__main__":
    ingest_standings()
