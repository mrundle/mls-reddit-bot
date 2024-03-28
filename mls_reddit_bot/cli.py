import argparse
import datetime
import dateutil
import os
import pytz

from mls_reddit_bot.main import main
from mls_reddit_bot.main import constants

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
    parser.add_argument("--data-directory",
                        default=constants.DEFAULT_DATA_DIR,
                        help="data directory")
    parser.add_argument("--categories",
                        default=constants.DEFAULT_MLS_CATEGORIES,
                        help="competition category")
    parser.add_argument("--show-timezones",
                        action='store_true',
                        help="list all valid timezone strings and exit")
    parser.add_argument("--show-categories",
                        action='store_true',
                        help="list all valid categories and exit")
    parser.add_argument("-f", "--force",
                        action='store_true',
                        help="force a fetch of fresh data; by default, this" \
                            "script prefers cached results")
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

    os.makedirs(args.data_directory, exist_ok=True)

    return args

def cli_main():
    args = parse_args()
    main(
        start=args.start,
        end=args.end,
        tz=args.tz,
        categories=args.categories,
        data_directory=args.data_directory,
        force=args.force,
    )
