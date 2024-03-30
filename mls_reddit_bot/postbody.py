"""
This file builds the main body of the reddit post.
"""

import pytz
import datetime

def get_submission_title(event):
    if event.minutes_til_start() > 0:
        postfix = 'Starting Soon'
    elif event.completed:
        postfix = 'Final'
    else:
        postfix = 'In Progress'
    return f'Match Thread: {event.away_team_fullname} @ {event.home_team_fullname} ({postfix})'

def _get_bot_footer():
    tz = pytz.timezone('US/Central')
    ts = datetime.datetime.now().astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    text = ''
    text += f'*u/MLS_Reddit_Bot is a bot utilizing ESPN APIs and AWS Lambda ([Github](https://github.com/mrundle/mls-reddit-bot)). Issues or feature requests can be submitted [here](https://github.com/mrundle/mls-reddit-bot/issues/new/choose). This post was last updated at {ts}.*'
    return text

def _get_key_event_text(event):
    text = ''
    text += f'**Match events via [ESPN](https://www.espn.com/soccer/match?gameId={event.id})**\n\n'
    for event in event.get_key_events():
        text += f'* {event}\n\n'
    return text

def _get_lineups(event):
    text = ''
    text += '**Lineups**\n\n'
    for roster in event.rosters:
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

def _get_match_summary(event, submission_id=None):
    text = '**Overview**\n\n'
    text += f'Matchup: {event.away_team_fullname} ({event.away_team_score()}) @ {event.home_team_fullname} ({event.home_team_score()})\n\n'
    if event and event.completed:
        text += f'Status: Full time\n\n'
    elif event.minutes_til_start > 0:
        text += f'Status: Starting soon\n\n'
    else:
        text += f'Status: In progress\n\n'
    text += f'Venue: {event.venue}, {event.city}\n\n'
    text += f'Start: {event.start_timestamp()}\n\n'
    if submission_id:
        text += f'\n♻️[ Auto-refreshing reddit comments link](http://www.reddit-stream.com/comments/{submission_id})\n\n'
    return text

def get_submission_body(event, submission_id=None):
    body = ''
    body += _get_match_summary(event, submission_id) + '\n\n'
    body += '___\n'
    body += _get_key_event_text(event) + '\n\n'
    body += '___\n'
    body += _get_lineups(event) + '\n\n'
    body += '___\n'
    body += _get_bot_footer() + '\n\n'
    return body
