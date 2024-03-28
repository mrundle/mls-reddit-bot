import warnings
warnings.filterwarnings('ignore')

# aws
import boto3
from botocore.exceptions import ClientError

import datetime
import json
import os
import requests

# installed via pip
import dateutil
import pytz

from mls_reddit_bot import constants
# this package
try:
    from mls_reddit_bot import log
except:
    import log


class MlsMatchSummary(object):
    def __init__(self, json_api_data, tz=constants.DEFAULT_TIMEZONE):
        self.data = json_api_data
        self.tz_str = tz
        # see ./schema-examples/match.json
        d = self.data
        self.id = d["optaId"]
        self.home_team = d["home"]["fullName"]
        self.away_team = d["away"]["fullName"]
        self.venue = d["venue"]["name"]
        self.city = d["venue"]["city"]
        if d["isTimeTbd"]:
            self.date = 'TBD'
        else:
            self.date = dateutil.parser.parse(d["matchDate"])

    def __repr__(self):
        """
        Return string like:
            Saturday March 23 2024, 08:30 PM EDT: D.C. United @ St. Louis CITY SC (CITYPARK, St. Louis, MO)
        """
        ts = self.start_timestamp()
        return f'{ts}: {self.away_team} @ {self.home_team} ({self.venue}, {self.city})'

    def start_timestamp(self):
        """
        Returns string like:
            Saturday March 23 2024, 07:30 PM CDT
        """
        tz = pytz.timezone(self.tz_str)
        dt = self.date.astimezone(tz=tz)
        return dt.strftime(f'%A %B %d %Y, %I:%M %p {dt.tzname()}')

    def minutes_til_start(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = self.date - now
        seconds_til_start = delta.total_seconds()
        minutes_til_start = int(seconds_til_start / 60)
        return minutes_til_start

    def is_ended(self):
        return self.data["is_final"]


# TODO use this, more granular stats
def fetch_match_details(id, outdir):
    outfile = os.path.join(outdir, f'match-{id}')
    url=f'https://stats-api.mlssoccer.com/v1/matches?&match_game_id={id}&include=away_club_match&include=home_club_match&include=venue&include=home_club&include=away_club'
    log.debug(f'fetching from {url}')
    response = requests.get(url)
    data = response.json()
    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4)
        log.debug(f'wrote details for match id {id} to {outfile}')


def fetch_matches(start_dt, end_dt, tz, categories, outdir, force):
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")

    data = {}

    s3 = boto3.client('s3')
    bucket = constants.AWS_S3_BUCKET_NAME
    key = f'mls-matches-{start_str}_{end_str}'
    data = {}

    try:
        result = s3.get_object(Bucket=bucket, Key=key)
        text = result["Body"].read().decode()
        data = json.loads(text)
    except ClientError as ex:
        pass

    # skip fetch if we already have, unless --force is requested
    if data and not force:
        log.debug(f'skipping fetch, data exists')
    else:
        # make the api call
        data = []
        url=f"https://sportapi.mlssoccer.com/api/matches?culture=en-us&dateFrom={start_str}&dateTo={end_str}"
        log.debug(f'fetching from {url}')
        response = requests.get(url)
        data = response.json()

        # write
        s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(data, indent=4))

    # filter
    result = []
    for match in data:
        try:
            if match["competition"]["slug"] in categories:
                result.append(MlsMatchSummary(match, tz=tz))
        except KeyError:
            log.warn("missing competition category slug")
            pass

    return result
