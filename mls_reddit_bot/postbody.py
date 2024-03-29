"""
This file builds the main body of the reddit post.
"""

import pytz
import datetime

def get_submission_title(mls_match, espn_event):
    if mls_match.minutes_til_start() > 0:
        postfix = 'Starting Soon'
    elif espn_event.is_completed():
        postfix = 'Final'
    else:
        postfix = 'In Progress'
    return f'Match thread: {mls_match.away_team_fullname} @ {mls_match.home_team_fullname} ({postfix})'

def _get_bot_footer():
    tz = pytz.timezone('US/Central')
    ts = datetime.datetime.now().astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    text = '___\n'
    text += f'*u/MLS_Reddit_Bot is a bot running via AWS Lambda ([github](https://github.com/mrundle/mls-reddit-bot)), utilizing MLS and ESPN APIs. Issues or feature requests can be submitted [here](https://github.com/mrundle/mls-reddit-bot/issues/new/choose). This post was last updated at {ts}.*'
    return text

def _get_espn_event_text(espn_event):
    text = '___\n'
    text += f'**Match events via [ESPN](https://www.espn.com/soccer/match?gameId={espn_event.id})**\n'
    for event in espn_event.get_key_events():
        text += f'* {event}\n'
    return text

def _get_lineups(espn_event):
    text = '___\n'
    text += '**Lineups**\n\n'
    for roster in espn_event.rosters:
        team = roster['team']['displayName']
        text += f'{team}\n\n'
        for player in roster['roster']:
            name = player['athlete']['displayName']
            position = player['position']['abbreviation']
            starter = player['starter'] # bool; but, already baked into position
            number = player['jersey']
            text += f'* {position} - {name}, #{number}\n'
        text += '\n'
    return text

def get_submission_body(mls_match, espn_event, submission_id=None):
    body = f'{str(mls_match)}\n\n'
    if submission_id:
        body = f'♻️[ Auto-refreshing reddit comments link](http://www.reddit-stream.com/comments/{submission_id})\n\n'
    body += _get_lineups(espn_event) + '\n\n'
    body += _get_espn_event_text(espn_event) + '\n\n'
    body += _get_bot_footer() + '\n\n'
    return body
