import gzip

from StringIO import StringIO

from urllib2 import Request, urlopen, URLError

import api_urls


def get_game_timestamps(id=None):
    url = api_urls.GAME_TIMESTAMPS.replace("<gamePk>", str(id))
    return get_url(url)


def get_game_at(id, timestamp):
    url = api_urls.GAME_TIMESTAMP.replace("<gamePk>", str(id))\
        .replace("<timeStamp>", str(timestamp))
    return get_url(url)


def get_game_diff(id, start, end):
    url = api_urls.GAME_DIFF.replace("<gamePk>", str(id))\
        .replace("<startTime>", str(start))\
        .replace("<endTime>", str(end))
    return get_url(url)


def get_game(id=None):
    url = api_urls.GAME.replace("<gamePk>", str(id))
    return get_url(url)


def get_game_boxscore(id=None):
    url = api_urls.GAME.replace("<gamePk>", str(id)) + "boxscore"
    return get_url(url)


def get_teams(id=None):
    url = api_urls.TEAM_LIST
    if id is not None:
        url += id
    return get_url(url)


def get_standings(date=None):
    url = api_urls.STANDINGS
    if date is not None:
        url += "?date=" + date
    return get_url(url)


def get_team_roster(id):
    url = api_urls.ROSTER_LIST.replace("<teamId>", str(id))
    return get_url(url)


def get_player(id=None, ids=None):
    if id is not None:
        url = api_urls.PLAYER_INFO + str(id)
    elif ids is not None:
        url = api_urls.PLAYER_INFO + "?personIds=" + ",".join(str(x) for x in ids)
    return get_url(url)


def get_schedule(id, season=None):
    url = api_urls.SCHEDULE_INFO + "?teamId=" + str(id)
    if season is not None:
        url += "&season=" + season
    return get_url(url)


def get_url(url):
    request = Request(url)
    request.add_header('Accept-encoding', 'gzip')
    try:
        response = urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            html = f.read()
        else:
            html = response.read()
    except URLError, e:
        print e
        return ""
    return html
