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
from mls_reddit_bot import constants
from mls_reddit_bot import ddb
from mls_reddit_bot import espn
from mls_reddit_bot import log
from mls_reddit_bot import mls
from mls_reddit_bot import reddit


def process_match(m, espn_scoreboard, reddit_cli, subreddit):
    if m.minutes_til_start() > constants.DEFAULT_MINUTES_TO_START:
        print(f'not processing {m}, minutes_til_start={m.minutes_til_start()}')
        return

    entry = ddb.DdbGameThread(m.id)
    if entry.error:
        log.error('failed to fetch game thread id from dynamodb')
        return
    submission_id = entry.get_reddit_thread_id() # thread_id
    if not submission_id:
        submission = subreddit.submit(
            title=f'Match thread: {m.away_team} @ {m.home_team}',
            selftext=str(m))
        if not entry.update_reddit_thread_id(submission.id):
            # s3 for backup? or query reddit for recently created
            log.error('failed to update ddb with reddit thread '
                      'for game id {m.id}, duplicates inbound...')
        log.info(f'Posted match thread for match id {m.id}: https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission.id}')
    else:
        """
        TODO:
            1. check if game is over; if so, mark as much in ddb so we
            can stop checking (or maybe just check espn scoreboard first)
            2. after game ends, maybe lock post and create post-match
            thread. similarly, ddb should be updated with this info
            3. for in-progress or newly ended games, update match thread
            with latest summary from MLS/ESPN

            4. Create helper function to build the post body of a thread
            based on MLS and ESPN data. The same function should be
            used whether creating or editing a thread.

        NOTE: Match thread might be created before ESPN has information.
        That's fine, just make sure the post doesn't get screwed up.
        """
        log.info(f'(TODO) Updating match thread for match id {m.id}: https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission_id}')
        new_post_body = f'UPDATED: {str(m)}'
        submission = reddit_cli.submission(submission_id)
        submission = submission.edit(new_post_body)


def process_matches(matches, scoreboard, reddit_cli, subreddit):
    for match in matches:
        process_match(match, scoreboard, reddit_cli, subreddit)

# TODO assert environment variables (e.g. for praw/reddit)
def main(
        start=constants.DEFAULT_WINDOW_START,
        end=constants.DEFAULT_WINDOW_END,
        tz=None,
        categories=None,
        data_directory=None,
        force_fetch_mls=None,
        prefer_cached_espn=None):
    if not tz:
        tz = constants.DEFAULT_TIMEZONE
    if not categories:
        categories = constants.DEFAULT_MLS_CATEGORIES
    if not data_directory:
        data_directory = constants.DEFAULT_DATA_DIR

    matches = mls.fetch_matches(
        start,
        end,
        tz,
        categories,
        data_directory,
        force_fetch_mls)

    if not matches:
        log.info('no matches detected, returning')

    scoreboard = espn.EspnLeagueScoreboard("usa.1", prefer_cached_espn) # mls
    reddit_cli = reddit.get_reddit_client()
    subreddit = reddit_cli.subreddit(reddit.REDDIT_SUBREDDIT)

    process_matches(matches, scoreboard, reddit_cli, subreddit)
