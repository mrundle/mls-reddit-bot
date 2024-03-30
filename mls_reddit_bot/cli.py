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
    parser.add_argument("--categories",
                        default=constants.DEFAULT_MLS_CATEGORIES,
                        help="competition category")
    parser.add_argument("--show-timezones",
                        action='store_true',
                        help="list all valid timezone strings and exit")
    parser.add_argument("--show-categories",
                        action='store_true',
                        help="list all valid categories and exit")
    parser.add_argument("--force-fetch-mls",
                        action='store_true',
                        default=False,
                        help="force fetch of MLS data (disabled by default)")
    parser.add_argument("--prefer-cached-espn",
                        action='store_true',
                        default=False,
                        help="try to use cached ESPN data (generally only for testing)")
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
    elif args.show_categories:
        print('CATEGORIES:')
        for cat in SUPPORTED_MLS_CATEGORIES:
            print(f'\t* {cat}')
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
        categories=args.categories,
        force_fetch_mls=args.force_fetch_mls,
        prefer_cached_espn=args.prefer_cached_espn,
    )
