import requests

import datetime
import dateutil
import json
import pytz

from mls_reddit_bot import aws
from mls_reddit_bot import constants
from mls_reddit_bot import log
from mls_reddit_bot import timezone


def url_fetch_json(url):
    for i in range(3):
        log.info(f'fetching from {url}')
        try:
            return requests.get(url, timeout=10).json()
        except requests.exceptions.Timeout:
            log.warn(f'request timed out')
    log.error(f'all requests timed out')
    return {}


class EspnEvent(object):
    def __init__(self, data, tz=constants.DEFAULT_TIMEZONE, prefer_cached=False):
        self.data = data
        self.tz_str = tz
        self.prefer_cached = prefer_cached
        self.id = data['id']
        self.tz = tz
        self.uid = data['uid']
        self.date_str = data['date']
        self.date = dateutil.parser.parse(data['date'])
        self.name = data['name'] # e.g. "D.C. United at St. Louis CITY SC"
        self.shortName = data['shortName'] # e.g. "DC @ STL"
        self.season = data['season']
        self.status = data['status']
        self.completed = data['status']['type']['completed']
        self.venue = data['competitions'][0]['venue']['fullName']
        self.city = data['competitions'][0]['venue']['address']['city']
        self.country = data['competitions'][0]['venue']['address']['country']
        self.display_clock = data['competitions'][0]['status']['displayClock']
        self.links = data['links']
        self.learned_tz = timezone.get_timezone(self.city)
        if not self.learned_tz:
            log.warn(f'could not learn timezone for {self.city}')

        for team in self.data['competitions'][0]['competitors']:
            if team['homeAway'].lower() == 'home':
                self.home_team_abbrev = team['team']['abbreviation']
                self.home_team_short = team['team']['shortDisplayName']
                self.home_team_fullname = team['team']['name']
            else:
                self.away_team_abbrev = team['team']['abbreviation']
                self.away_team_short = team['team']['shortDisplayName']
                self.away_team_fullname = team['team']['name']

        # fetch summary
        self.summary = self.fetch()

        if self.summary:
            self.header = self.get_header() # grab summary.competitions.header[0]
            self.rosters = self.summary.get('rosters', [])
        else:
            self.header = {}
            self.rosters = {}


    def fetch(self):
        # fetches match summary, which has the following top-level keys
        #    article,    boxscore,  broadcasts, commentary
        #    format,     gameInfo,  hasOdds,    headToHeadGames,
        #    header,     keyEvents, news,       odds,
        #    pickcenter, rosters,   standings, videos
        data = {}
        # TODO not hardcode usa.1 (if ever supporting non-mls)
        self.url = f'http://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/summary?event={self.id}'
        s3_bucket = constants.AWS_S3_BUCKET_NAME
        s3_subdir = constants.AWS_S3_ESPN_SCOREBOARD_SUBDIR
        s3_file = f'cached-event-summary-{self.id}.json'
        if self.prefer_cached:
            return aws.s3.read_or_fetch_json(self.url, s3_bucket, f'{s3_subdir}/{s3_file}')
        else:
            data = url_fetch_json(self.url)


    def __repr__(self):
        """
        Return string like:
            DC @ STL
        """
        return f'{self.shortName} {self.date_str} in {self.city} at {self.start_timestamp()} (id={self.id})'

    def start_timestamp(self):
        """
        Returns string like:
            Saturday March 23 2024, 07:30 PM CDT
        """
        tz = self.learned_tz if self.learned_tz else pytz.timezone(self.tz_str)
        dt = self.date.astimezone(tz=tz)
        return dt.strftime(f'%A %B %d %Y, %I:%M %p {dt.tzname()}')

    def minutes_til_start(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = self.date - now
        seconds_til_start = delta.total_seconds()
        minutes_til_start = int(seconds_til_start / 60)
        return minutes_til_start

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
                return team.get('score', 0)

    def away_team_score(self):
        for team in self.header['competitors']:
            if team['homeAway'].lower() == 'away':
                return team.get('score', 0)
