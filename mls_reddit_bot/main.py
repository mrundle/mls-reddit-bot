#!/usr/bin/env python3

DESCRIPTION = f"""\
This script fetches match details from the public MLS API for a given period
of time. By default, it will use a window of -2 days and +5. To accept defaults,
you can run the script with no arguments.

As of writing, the MLS API is not publicly documented or committed to be
maintained in its current form. API changes may change without warning, which
will break this script. The MLS API currently also does not require
authentication, which is something else that could change in the future.

This script attempts to make as few calls as possible to the API. Results are
cached for multiple repeated calls.
"""

import warnings
warnings.filterwarnings('ignore')

import datetime
import os
import sys

# this package
import mls_reddit_bot as mls
from mls_reddit_bot import log

# general
DEFAULT_DATA_DIR = '/tmp'
DEFAULT_TIMEZONE = 'US/Eastern'
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True) # TODO remove, not used


# TODO verify environment variables
def main():
    reddit_cli = mls.reddit.get_reddit_client()
    subreddit = reddit_cli.subreddit(mls.reddit.REDDIT_SUBREDDIT)

    start = datetime.date.today() - datetime.timedelta(days=2)
    end = datetime.date.today() + datetime.timedelta(days=5)
    tz = DEFAULT_TIMEZONE
    categories = mls.mls.DEFAULT_CATEGORIES
    data_directory = DEFAULT_DATA_DIR
    force = False

    matches = mls.mls.fetch_matches(
        start,
        end,
        tz,
        categories,
        data_directory,
        force)

    for m in matches:
        print(m)
        if m.starts_in_n_minutes(5):
            """
            TODO:
                1. Record created match threads (by id) in AWS DDB.
                2. Keep attempting creation until success.
                3. After match finishes, lock post and create post-match thread.
                (Maybe)
                4. Eventually: Log game stats and updates to each game thread,
                via integration with fetch_match_details()
                5. Move helper code into the lambda layer, clean up function.
            """
            log.debug(f'Posting match thread for match id {m.id}')
            submission = subreddit.submit(
                title=f'Match thread: {m.away_team} @ {m.home_team}',
                selftext=str(m))
            log.debug(f'Posted match thread https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission}')

def lambda_handler(event, context):
    try:
        main()
        return {
            'statusCode': 200,
            'body': 'OK',
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e),
        }

if __name__ == '__main__':
    main()
