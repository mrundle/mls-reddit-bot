import datetime
import os

# aws resources
AWS_DDB_TABLE_NAME = 'mls-matches'
AWS_S3_BUCKET_NAME = 'mls-reddit-bot'
AWS_S3_MATCH_DATA_SUBDIR = 'mls-match-data'
AWS_S3_ESPN_SCOREBOARD_SUBDIR = 'espn-scoreboard' # caching disabled outside of --force testing, freshness is important here

# use eastern time by default (TODO try to use local timezone per match)
DEFAULT_TIMEZONE = 'US/Eastern'

# create threads this many minutes before the match is scheduled to start
DEFAULT_MINUTES_TO_START = 15

# TODO remove local data dir, use s3/ddb for all persistence
DEFAULT_DATA_DIR = '/tmp'
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True) # TODO remove, not used

# by default, look for matches occurring +/- a certain window relative to today
TODAY = datetime.date.today()
DEFAULT_WINDOW_START = TODAY - datetime.timedelta(days=2)
DEFAULT_WINDOW_END = TODAY + datetime.timedelta(days=5)

# opt in to these categories by default
DEFAULT_MLS_CATEGORIES = [ # match["competition"]["slug"]
    "mls-regular-season",
    "mls-cup-playoffs",
    "mls-all-star-game",
]

# these are all supported game categories through mls
SUPPORTED_MLS_CATEGORIES = [
    "campeones-cup",
    "canadian-championship",
    "concacaf-champions-league",
    "concacaf-nations-league",
    "friendly",
    "gold-cup",
    "international-friendly",
    "leagues-cup",
    "mls-all-star-game",
    "mls-cup-playoffs",
    "mls-regular-season",
    "other-club-friendlies",
    "u-s-open-cup"
]
