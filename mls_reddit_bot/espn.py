#!/usr/bin/env python3
# fetch all games
#    https://site.web.api.espn.com/apis/v2/scoreboard/header?region=us&lang=en&contentorigin=espn&buyWindow=1m&showAirings=buy,live,replay&showZipLookup=true&tz=America/New_York&_ceID=15878776

import json
import os
import requests

# pip
import dateutil

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


# if we haven't cached already, fetch json from a url
def read_or_fetch_json(url, cachefile_basename):
    cache_dir = '/tmp/cached/'
    os.makedirs(cache_dir, exist_ok=True)
    cachefile = os.path.join(cache_dir, cachefile_basename)

    data = {}
    try:
        with open(cachefile, 'r') as f:
            data = json.load(f)
    except Exception as e:
        pass

    if not data:
        response = requests.get(url)
        data = response.json()
        with open(cachefile, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"wrote {cachefile} from fetched {url}")
    return data


class EspnEvent(object):
    def __init__(self, data):
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

        # fetch summary
        self.summary = self.fetch()
        self.header = self.get_header()

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
        self.url = f'http://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/summary?event={self.id}'
        cachefile = f'cached-event-summary-{self.id}.json'
        return read_or_fetch_json(self.url, cachefile)

    def print_verbose_commentary(self):
        commentary = self.summary['commentary']
        for item in commentary:
            sequence = item['sequence']
            text = item['text']
            time = item['time']['displayValue']
            print(f'{time}: {text}')

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

        #details = self.header['details']
        teams = self.header['competitors']
        summary_text = ''
        t0 = self.header['competitors'][0]
        t0_abbrev = t0['team']['displayName']
        t0_score = t0['score']
        t1 = self.header['competitors'][1]
        t1_abbrev = t1['team']['displayName']
        t1_score = t1['score']

        prefix = 'Final' if completed else 'In Progress' # TODO time
        print(f'{prefix}: {t0_abbrev} ({t0_score}) vs. {t1_abbrev} ({t1_score})')


class EspnLeagueScoreboard(object):
    def __init__(self, league_code):
        assert league_code in ESPN_SOCCER_LEAGUE_CODES.keys()
        self.league_code = league_code
        self.url = f'http://site.api.espn.com/apis/site/v2/sports/soccer/{self.league_code}/scoreboard'
        self.data = read_or_fetch_json(self.url, f'cached-scoreboard-{league_code}.json')
        self.leagues = self.data['leagues'] # not much here, mainly logos
        # "season": {
        #     "type": 12328,
        #     "year": 2024
        # }
        self.season = self.data['season']
        self.day = dateutil.parser.parse(self.data['day']['date']) # e.g. 2024-03-23
        self.events = [
            EspnEvent(e) for e in self.data['events']
        ]


# local testing
if __name__ == '__main__':
    scoreboard = EspnLeagueScoreboard("usa.1")
    for event in scoreboard.events:
        if 'stl' in event.shortName.lower():
            with open('cached-event.json', 'w') as f:
                json.dump(event.data, f, indent=4)
            #event.print_verbose_commentary()
            event.print_header()
            event.print_key_events()
