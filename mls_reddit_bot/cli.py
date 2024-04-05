import argparse
import datetime
import dateutil
import os
import pytz

from mls_reddit_bot.main import main
from mls_reddit_bot import constants

def get_cli_description():
    return """\
TODO: Come up with a better description
"""

def parse_args():
    parser = argparse.ArgumentParser(
        description=get_cli_description(),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    today = datetime.date.today()
    parser.add_argument("--start",
                        default=str(constants.DEFAULT_WINDOW_START),
                        type=str,
                        help="start date")
    parser.add_argument("--end",
                        default=str(constants.DEFAULT_WINDOW_END),
                        type=str,
                        help="start date")
    parser.add_argument("--tz",
                        default=constants.DEFAULT_TIMEZONE,
                        type=str,
                        help="output timezone")
    parser.add_argument("--show-timezones",
                        action='store_true',
                        help="list all valid timezone strings and exit")
    parser.add_argument("--prefer-cached-espn",
                        action='store_true',
                        default=False,
                        help="try to use cached ESPN data (generally only for testing)")
    parser.add_argument("--minutes-early",
                        default=constants.DEFAULT_MINUTES_TO_START,
                        type=int,
                        help="post the match thread N minutes before match start")
    parser.add_argument("--espn-match-id",
                        help="Run for a specific match id")
    parser.add_argument("--subreddit",
                        default=constants.REDDIT_SUBREDDIT,
                        help="subreddit to post to")
    parser.add_argument("--dry-run",
                        action='store_true',
                        default=False,
                        help="Don't actually post to reddit")
    parser.add_argument("--force-update",
                        action='store_true',
                        default=False,
                        help="force update of reddit thread even if match is complete")
    #parser.add_argument("-d", "--debug",
    #                    action='store_true',
    #                    help="show debug log messages")
    args = parser.parse_args()
    args.start = dateutil.parser.parse(args.start)
    args.end = dateutil.parser.parse(args.end)

    if args.show_timezones:
        print('TIMEZONES:')
        for tz in pytz.all_timezones_set:
            print(f'\t* {tz}')
        sys.exit(1)

    try:
        pytz.timezone(args.tz)
    except pytz.exceptions.UnknownTimeZoneError as e:
        sys.stderr.write(f"unknown timezone '{args.tz}', try {sys.argv[0]} --show-timezones\n")
        sys.exit(1)

    return args

def cli_main():
    args = parse_args()
    main(
        start=args.start,
        end=args.end,
        tz=args.tz,
        subreddit_name=args.subreddit,
        minutes_early=args.minutes_early,
        prefer_cached_espn=args.prefer_cached_espn,
        espn_match_id=args.espn_match_id,
        dryrun=args.dry_run,
        force_update=args.force_update,
    )
