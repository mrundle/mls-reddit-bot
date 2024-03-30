import warnings
warnings.filterwarnings('ignore')

import json
import praw
import traceback

# this package
from mls_reddit_bot import (
    aws,
    constants,
    espn,
    log,
    postbody,
    reddit,
)


def process_match(event, reddit_cli, subreddit, minutes_early):
    if event.minutes_til_start() > minutes_early:
        print(f'not processing {event}, minutes_til_start={event.minutes_til_start()}')
        return

    ddb_entry = aws.ddb.DdbGameThread(event)
    if ddb_entry.error:
        log.error('failed to fetch game thread id from dynamodb')
        return

    submission_id = ddb_entry.get_reddit_thread_id() # thread_id
    submission_title = postbody.get_submission_title(event)
    submission_body = postbody.get_submission_body(event)

    if not submission_id:
        submission = subreddit.submit(title=submission_title, selftext=submission_body)
        if not ddb_entry.update_reddit_thread_id(submission.id):
            # TODO: s3 for backup? or query reddit for recently created
            # for now, write a fresh copy every time, but we should refuse to write
            # if the new text is significantly (or any) shorter than the old
            log.error('failed to update ddb with reddit thread '
                      'for {event}, duplicates inbound...')
        log.info(f'Posted match thread for {event}: https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission.id}')
    else:
        """
        TODO:
            1. after game ends, maybe lock post and create post-match
            thread. similarly, ddb should be updated with this info
        """
        if ddb_entry.is_game_completed():
            log.info(f'Game completed, skipping match thread update for {event}: https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission_id}')
            return
        log.info(f'Updating match thread for {event}: https://www.reddit.com/r/MLS_Reddit_Bot/comments/{submission_id}')
        # now that we have the submission_id, recreate the body
        submission_body = postbody.get_submission_body(event, submission_id)
        submission = reddit_cli.submission(submission_id)
        try:
            submission = submission.edit(submission_body)
        except praw.exceptions.RedditAPIException as e:
            log.error(f'failed to update {event}, reddit exception: {e}')
        if event.completed:
            log.info(f'Match {event} is completed, posted final update')
            ddb_entry.set_game_completed()


def main(
            start=constants.DEFAULT_WINDOW_START,
            end=constants.DEFAULT_WINDOW_END,
            tz=constants.DEFAULT_TIMEZONE,
            minutes_early=constants.DEFAULT_MINUTES_TO_START,
            categories=constants.DEFAULT_MLS_CATEGORIES,
            force_fetch_mls=False,
            prefer_cached_espn=False
        ):

    scoreboard = espn.league.EspnLeagueScoreboard(
        "usa.1", # mls
        start=start,
        end=end,
        tz=tz,
        prefer_cached=prefer_cached_espn,
    )

    reddit_cli = reddit.client.get_reddit_client()
    subreddit = reddit_cli.subreddit(constants.REDDIT_SUBREDDIT)

    for event in scoreboard.events:
        try:
            process_match(event, reddit_cli, subreddit, minutes_early)
        except Exception as e:
            log.exception(f'caught error while handling {event}', e)
            exit(1)
