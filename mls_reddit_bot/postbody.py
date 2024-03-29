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
    return f'Match Thread: {mls_match.away_team_fullname} @ {mls_match.home_team_fullname} ({postfix})'

def _get_bot_footer():
    tz = pytz.timezone('US/Central')
    ts = datetime.datetime.now().astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    text = ''
    text += f'*u/MLS_Reddit_Bot is a bot running via AWS Lambda ([github](https://github.com/mrundle/mls-reddit-bot)), utilizing MLS and ESPN APIs. Issues or feature requests can be submitted [here](https://github.com/mrundle/mls-reddit-bot/issues/new/choose). This post was last updated at {ts}.*'
    return text

def _get_espn_event_text(espn_event):
    text = ''
    text += f'**Match events via [ESPN](https://www.espn.com/soccer/match?gameId={espn_event.id})**\n\n'
    for event in espn_event.get_key_events():
        text += f'* {event}\n\n'
    return text

def _get_lineups(espn_event):
    text = ''
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

def _get_match_summary(mls_match, espn_event, submission_id=None):
    text = '**Overview**\n\n'
    if espn_event:
        text += f'Matchup: {mls_match.away_team_fullname} ({espn_event.away_team_score()}) @ {mls_match.home_team_fullname} ({espn_event.home_team_score()})\n\n'
    else:
        text += f'Matchup: {mls_match.away_team_fullname} @ {mls_match.home_team_fullname}\n\n'
    if espn_event and espn_event.is_completed():
        text += f'Status: Full time\n\n'
    elif mls_match.minutes_til_start > 0:
        text += f'Status: Starting soon\n\n'
    else:
        text += f'Status: In progress\n\n'
    text += f'Venue: {mls_match.venue}, {mls_match.city}\n\n'
    text += f'Start: {mls_match.start_timestamp()}\n\n'
    if submission_id:
        text += f'\n♻️[ Auto-refreshing reddit comments link](http://www.reddit-stream.com/comments/{submission_id})\n\n'
    return text

def get_submission_body(mls_match, espn_event, submission_id=None):
    body = ''
    body += _get_match_summary(mls_match, espn_event, submission_id) + '\n\n'
    body += '___\n'
    if espn_event:
        body += _get_espn_event_text(espn_event) + '\n\n'
        body += '___\n'
        body += _get_lineups(espn_event) + '\n\n'
        body += '___\n'
    body += _get_bot_footer() + '\n\n'
    return body
