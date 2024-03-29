# fetch all games
#    https://site.web.api.espn.com/apis/v2/scoreboard/header?region=us&lang=en&contentorigin=espn&buyWindow=1m&showAirings=buy,live,replay&showZipLookup=true&tz=America/New_York&_ceID=15878776

# another one:
#    https://site.web.api.espn.com/apis/site/v2/sports/soccer/scorepanel?league=all&region=us&lang=en&contentorigin=espn&limit=250&dates=20240323&showAirings=live

# fetch mls (usa.1) teams
#     https://site.web.api.espn.com/apis/site/v2/sports/soccer/USA.1/teams?region=us&lang=en&contentorigin=espn&limit=400&includeModules=news

import json
import os
import requests

# pip
import dateutil

from mls_reddit_bot import constants
from mls_reddit_bot import s3
try:
    from mls_reddit_bot import log
except:
    import log


# can be found here https://www.espn.com/soccer/competitions
ESPN_SOCCER_LEAGUE_CODES = {
    "usa.1":          "MLS",
    "USA.NWSL":       "NWSL",
    "uefa.champions": "UEFA Champions League",
    "usa.open":       "U.S. Open Cup",
    "concacaf.leagues.cup": "Leagues Cup",
    "concacaf.league":      "Concacaf League",
    "usa.usl.l1":           "USL League One",
    "usa.usl.1":            "USL Championship",
}

def url_fetch_json(url):
    log.info(f'fetching from {url}')
    return requests.get(url).json()


class EspnEvent(object):
    def __init__(self, data, prefer_cached=False):
        self.data = data
        self.id = data['id']
        self.uid = data['uid']
        self.date = data['date']
        self.name = data['name']
        self.shortName = data['shortName']
        self.season = data['season']
        self.competitions = data['competitions']
        self.status = data['status']
        self.venue = data['venue']
        self.links = data['links']
        self.prefer_cached = prefer_cached
        # espn event: .competitions[0].competitors[0].team.abbreviation
        for team in self.competitions[0]['competitors']:
            if team['homeAway'].lower() == 'home':
                self.home_team_abbrev = team['team']['abbreviation']
                self.home_team_short = team['team']['shortDisplayName']
            else:
                self.away_team_abbrev = team['team']['abbreviation']
                self.away_team_short = team['team']['shortDisplayName']

        # fetch summary
        self.summary = self.fetch()
        self.header = self.get_header()
        self.rosters = self.summary.get('rosters', [])

    def fetch(self):
        # fetches match summary, which has the following top-level keys
        #     article
        #     boxscore
        #     broadcasts
        #     commentary
        #     format
        #     gameInfo
        #     hasOdds
        #     headToHeadGames
        #     header
        #     keyEvents
        #     news
        #     odds
        #     pickcenter
        #     rosters
        #     standings
        #     videos
        data = {}
        # TODO not hardcode usa.1 (if ever supporting non-mls)
        self.url = f'http://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/summary?event={self.id}'
        s3_bucket = constants.AWS_S3_BUCKET_NAME
        s3_subdir = constants.AWS_S3_ESPN_SCOREBOARD_SUBDIR
        s3_file = f'cached-event-summary-{self.id}.json'
        if self.prefer_cached:
            return s3.read_or_fetch_json(self.url, s3_bucket, f'{s3_subdir}/{s3_file}')
        else:
            return url_fetch_json(self.url)

    def is_completed(self):
        return self.status['type']['completed']

    def print_verbose_commentary(self):
        commentary = self.summary['commentary']
        for item in commentary:
            sequence = item['sequence']
            text = item['text']
            time = item['time']['displayValue']
            print(f'{time}: {text}')

    def get_key_events(self):
        event_strings = []
        for event in self.summary['keyEvents']:
            time = event['clock']['displayValue']
            try:
                text = event['text']
            except KeyError:
                text = event['type']['text']
            try:
                typetext = event['type']['text'].lower()
            except:
                typetext = ''
            try:
                scoring = event['scoringPlay']
            except KeyError:
                scoring = False
            event_str = ''
            if time:
                event_str += f'**{time}** '
            if scoring:
                event_str += '⚽ '
            if 'substitution' in typetext:
                event_str += '🔄 '
            if 'red card' in typetext:
                event_str += '🟥 '
            if 'yellow card' in typetext:
                event_str += '🟨 '
            event_str += text
            event_strings.append(event_str)
        return event_strings

    def print_key_events(self):
        print('Key events:')
        events = self.summary['keyEvents']
        for event in events:
            time = event['clock']['displayValue']
            try:
                text = event['text']
            except KeyError:
                text = event['type']['text']
            event_str = '* '
            if time:
                event_str += f'{time} '
            event_str += text
            print(event_str)

    def get_header(self):
        header = {}
        competitions = self.summary['header']['competitions']
        if len(competitions) != 1:
            print(f'warning: weird number of competitions ({len(competitions)})')
        for competition in competitions:
            if competition['id'] == self.id:
                return competition
        return {}

    def print_header(self):
        # competition header includes:
        #     boxscoreAvailable
        #     boxscoreSource
        #     broadcasts
        #     commentaryAvailable
        #     competitors
        #     conferenceCompetition
        #     date
        #     details
        #     groups
        #     id
        #     liveAvailable
        #     neutralSite
        #     notes
        #     onWatchESPN
        #     playByPlaySource
        #     recent
        #     status
        #     uid
        if not self.header['boxscoreAvailable']:
            print('no box score available')
            return

        completed = self.header['status']['type']['completed']

        summary_text = ''
        t0 = self.header['competitors'][0]
        t0_abbrev = t0['team']['displayName']
        t0_score = t0.get('score', 'NaN')
        t1 = self.header['competitors'][1]
        t1_abbrev = t1['team']['displayName']
        t1_score = t1.get('score', 'NaN')

        prefix = 'Final' if completed else 'In Progress' # TODO time
        print(f'{prefix}: {t0_abbrev} ({t0_score}) vs. {t1_abbrev} ({t1_score})')


    def home_team_score(self):
        for team in self.header['competitors']:
            if team['homeAway'].lower() == 'home':
                return team['score']

    def away_team_score(self):
        for team in self.header['competitors']:
            if team['homeAway'].lower() == 'away':
                return team['score']


class EspnLeagueScoreboard(object):
    def __init__(self, league_code, start=None, end=None, prefer_cached=False):
        assert league_code in ESPN_SOCCER_LEAGUE_CODES.keys()
        self.league_code = league_code
        self.url = f'http://site.api.espn.com/apis/site/v2/sports/soccer/{self.league_code}/scoreboard'
        if start or end:
            if not (start and end):
                raise Exception('cannot specify only one of start/end')
            fmt = '%Y%m%d' # format used by ESPN's api, i.e. YYYYMMDD
            self.url += f'?dates={start.strftime(fmt)}-{end.strftime(fmt)}'
            self.start = start
            self.end = end
        s3_bucket = constants.AWS_S3_BUCKET_NAME
        s3_subdir = constants.AWS_S3_ESPN_SCOREBOARD_SUBDIR
        s3_file = f'cached-scoreboard-{league_code}-{start.strftime("%Y%m%d")}-{end.strftime("%Y%m%d")}.json'
        s3_key = f'{s3_subdir}/{s3_file}'
        self.prefer_cached = prefer_cached
        if self.prefer_cached:
            self.data = s3.read_or_fetch_json(self.url, s3_bucket, s3_key)
        else:
            self.data = url_fetch_json(self.url)
            s3.write_json(s3_bucket, s3_key, self.data)
        self.leagues = self.data['leagues'] # not much here, mainly logos
        # "season": {
        #     "type": 12328,
        #     "year": 2024
        # }
        #self.season = self.data['season']
        self.season = self.leagues[0]['season']
        #self.day = dateutil.parser.parse(self.data['day']['date']) # e.g. 2024-03-23
        self.events = [
            EspnEvent(e, self.prefer_cached) for e in self.data['events']
        ]
