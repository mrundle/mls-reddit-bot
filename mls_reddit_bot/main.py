#!/usr/bin/env python3

# TODO move description to README.md, a lot of this is leftover from an early CLI version
DESCRIPTION = f"""\
This program fetches match details from the public MLS API for a given period
of time. By default, it will use a window of -2 days and +5. To accept defaults,
you can run the script with no arguments.

As of writing, the MLS API is not publicly documented or committed to be
maintained in its current form. API changes may change without warning, which
will break this script. The MLS API currently also does not require
authentication, which is something else that could change in the future.

This script attempts to make as few calls as possible to the API. Results are
cached to/from S3 for multiple repeated calls over the same window.
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


# TODO assert environment variables (e.g. for praw/reddit)
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

    scoreboard = mls.espn.EspnLeagueScoreboard("usa.1") # mls

    for m in matches:
        print(m)
        if m.is_under_n_minutes_to_start(15):
            entry = mls.ddb.DdbGameThread(m.id)
            if entry.error:
                continue
            tid = entry.get_reddit_thread_id()
            if not tid:
                log.debug(f'Posting match thread for match id {m.id}')
                submission = subreddit.submit(
                    title=f'Match thread: {m.away_team} @ {m.home_team}',
                    selftext=str(m))
                if not entry.update_reddit_thread_id(submission):
                    # s3 for backup? or query reddit for recently created
                    log.error('failed to update ddb with reddit thread '
                              'for game id {m.id}, duplicates inbound...')
                log.debug(f'Posted match thread https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission}')
            else:
                """
                TODO:
                    1. check if game is over; if so, mark as much in ddb so we
                    can stop checking (or maybe just check espn scoreboard first)
                    2. after game ends, maybe lock post and create post-match
                    thread. similarly, ddb should be updated with this info
                    3. for in-progress or newly ended games, update match thread
                    with latest summary from MLS/ESPN

                NOTE: Match thread might be created before ESPN has information.
                That's fine, just make sure the post doesn't get screwed up.
                """
