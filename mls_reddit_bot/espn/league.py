from mls_reddit_bot import aws
from mls_reddit_bot import constants
from mls_reddit_bot import log
from mls_reddit_bot.espn.event import EspnEvent

import dateutil
import requests


def url_fetch_json(url):
    for i in range(3):
        log.info(f'fetching from {url}')
        try:
            return requests.get(url, timeout=10).json()
        except requests.exceptions.Timeout:
            log.warn(f'request timed out')
    log.error(f'all requests timed out')
    return {}


class EspnLeagueScoreboard(object):
    def __init__(
            self,
            league_code,
            start=None,
            end=None,
            tz=constants.DEFAULT_TIMEZONE,
            prefer_cached=False,
            espn_match_id=None):
        assert league_code in constants.ESPN_SOCCER_LEAGUE_CODES.keys()
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
            self.data = aws.s3.read_or_fetch_json(self.url, s3_bucket, s3_key)
        else:
            self.data = url_fetch_json(self.url)
        self.leagues = self.data['leagues'] # not much here, mainly logos
        self.season = self.leagues[0]['season']
        #self.day = dateutil.parser.parse(self.data['day']['date']) # e.g. 2024-03-23

        if espn_match_id:
            events_to_fetch = [e for e in self.data['events'] if str(e['id']) == str(espn_match_id)]
        else:
            events_to_fetch = self.data['events']
        self.events = [
            EspnEvent(e, tz=tz, prefer_cached=self.prefer_cached) for e in events_to_fetch
        ]
