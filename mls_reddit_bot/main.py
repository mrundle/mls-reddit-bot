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


def process_match(event, reddit_cli, subreddit, minutes_early, dryrun=False, force_update=False):
    if event.minutes_til_start() > minutes_early:
        log.info(f'not processing {event}, minutes_til_start={event.minutes_til_start()}')
        return

    ddb_entry = aws.ddb.DdbGameThread(event)
    if ddb_entry.error:
        log.error('failed to fetch game thread id from dynamodb')
        return

    submission_id = ddb_entry.get_reddit_thread_id() # thread_id
    submission_title = postbody.get_submission_title(event)
    submission_body = postbody.get_submission_body(event)

    if not submission_id:
        if dryrun:
            log.info(f'DRYRUN: Would have posted match thread for {event}')
            return
        submission = subreddit.submit(title=submission_title, selftext=submission_body)
        if not ddb_entry.update_reddit_thread_id(submission.id):
            # TODO: s3 for backup? or query reddit for recently created
            # for now, write a fresh copy every time, but we should refuse to write
            # if the new text is significantly (or any) shorter than the old
            log.error('failed to update ddb with reddit thread '
                      'for {event}, duplicates inbound...')
        log.info(f'Posted match thread for {event}: https://www.reddit.com/r/{subreddit.display_name}/comments/{submission.id}')
    else:
        """
        TODO: Potentially lock post and create post-match thread.
        Post-match thread should be linked in overview and added as a comment.
        Post-match thread should be tagged to the DDB match entry.
        """
        if ddb_entry.is_game_completed() and not force_update:
            log.info(f'Game completed, skipping match thread update for {event}: https://www.reddit.com/{submission_id}')
            return
        elif dryrun:
            log.info(f'DRYRUN: Would have updated match thread for {event} to https://www.reddit.com/{submission_id}')
        else:
            log.info(f'Updating match thread for {event}: https://www.reddit.com/{submission_id}')
            # now that we have the submission_id, recreate the body
            submission_body = postbody.get_submission_body(event, submission_id)
            submission = reddit_cli.submission(submission_id)
            try:
                submission = submission.edit(submission_body)
            except praw.exceptions.RedditAPIException as e:
                log.exception(f'failed to update reddit for {event}')

        if event.completed:
            if dryrun:
                log.info(f'DRYRUN: Match completed, would have been final update for {event}')
            else:
                log.info(f'Match {event} is completed, posted final update')
                ddb_entry.set_game_completed()


def main(
            start=constants.DEFAULT_WINDOW_START,
            end=constants.DEFAULT_WINDOW_END,
            tz=constants.DEFAULT_TIMEZONE,
            subreddit_name=constants.REDDIT_SUBREDDIT,
            minutes_early=constants.DEFAULT_MINUTES_TO_START,
            categories=constants.DEFAULT_MLS_CATEGORIES,
            prefer_cached_espn=False,
            espn_match_id=None,
            dryrun=False,
            force_update=False,
            debug=False,
        ):

    log.setup_logger(debug=debug)

    reddit_cli = reddit.client.get_reddit_client()
    subreddit = reddit_cli.subreddit(subreddit_name)
    log.info(f'Subreddit: r/{subreddit_name}')

    scoreboard = espn.league.EspnLeagueScoreboard(
        "usa.1", # mls
        start=start,
        end=end,
        tz=tz,
        prefer_cached=prefer_cached_espn,
        espn_match_id=espn_match_id,
    )

    for event in scoreboard.events:
        if espn_match_id and espn_match_id != event.id:
            continue
        try:
            process_match(
                event,
                reddit_cli,
                subreddit,
                minutes_early,
                dryrun=dryrun,
                force_update=force_update)
        except Exception as e:
            log.exception(f'caught error while handling {event}')
            exit(1)
