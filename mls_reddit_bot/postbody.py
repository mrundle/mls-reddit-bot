"""
This file builds the main body of the reddit post.
"""

import pytz
import datetime

def get_submission_title(event):
    return f'Match Thread: {event.away_team_fullname} @ {event.home_team_fullname}'

def _get_bot_footer():
    tz = pytz.timezone('US/Central')
    ts = datetime.datetime.now().astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    text = ''
    text += f'^(This thread is managed by a bot running on AWS Lambda and using ESPN APIs. Issues or feature requests can be submitted) [^( via github.)](https://github.com/mrundle/mls-reddit-bot/issues/new/choose) ^(This post was last updated at {ts}.)'
    return text

def _get_key_event_text(event):
    text = ''
    text += f'**Match events via [ESPN](https://www.espn.com/soccer/match?gameId={event.id})**\n\n'
    events = event.get_key_events()
    if events:
        for event in event.get_key_events():
            text += f'* {event}\n\n'
    else:
        text += '*Not yet available*\n\n'
    return text

def _player_str(player):
    if not player:
        return ''
    name = player['athlete']['displayName']
    position = player['position']['abbreviation']
    starter = player['starter'] # bool; but, already baked into position
    number = player['jersey']
    return f'{name}, #{number}|{position}'

def _get_lineups(event):
    text = '**Lineups**\n\n'
    try:
        team_a = event.rosters[0]['team']['displayName']
        team_b = event.rosters[1]['team']['displayName']
        players_a = list(reversed(event.rosters[0]['roster']))
        players_b = list(reversed(event.rosters[1]['roster']))
        text += f'| |**{team_a}**|Pos| |**{team_b}**|Pos|\n'
        text += f'|-|:-----------|:--|-|:-----------|:--|{team_b}|\n'
        while players_a or players_b:
            a = None if not players_a else players_a.pop()
            b = None if not players_b else players_b.pop()
            text += f'||{_player_str(a)}||{_player_str(b)}|\n'
        text += '\n'
    except:
        text += '*Not yet available*\n\n'
    return text

def _get_match_summary(event, submission_id=None):
    text = '**Overview**\n\n'
    text += f'|||⚽|\n'
    text += '|---|:---:|:-:|\n'
    text += f'|**Home**|**{event.home_team_fullname}**|**{event.home_team_score()}**|\n'
    text += f'|**Away**|**{event.away_team_fullname}**|**{event.away_team_score()}**|\n'
    text += f'|Status|{event.display_status}||\n'
    text += f'|Venue|{event.venue}||\n'
    text += f'|City|{event.city}||\n'
    text += f'|Date|{event.start_day()}||\n'
    text += f'|Time|{event.start_time()}||\n\n'
    if submission_id:
        text += f'\n♻️[ Auto-refreshing reddit comments link](http://www.reddit-stream.com/comments/{submission_id})\n\n'
    return text

def _get_pre_match_summary(event, submission_id=None):
    text = '**Overview**\n\n'
    text += '*Match details not yet available via ESPN.*\n\n'
    text += f'|||⚽|\n'
    text += '|---|:---:|:-:|\n'
    text += f'|**Home**|**{event.home_team_fullname}**|**-**|\n'
    text += f'|**Away**|**{event.away_team_fullname}**|**-**|\n'
    text += f'|Venue|{event.venue}, {event.city}||\n'
    text += f'|Start|{event.start_timestamp()}||\n\n'
    if submission_id:
        text += f'\n♻️[ Auto-refreshing reddit comments link](http://www.reddit-stream.com/comments/{submission_id})\n\n'
    return text

def get_submission_body(event, submission_id=None):
    body = ''
    if not event.summary:
        body += _get_pre_match_summary(event, submission_id)
    else:
        body += _get_match_summary(event, submission_id) + '\n\n'
        body += '___\n'
        body += _get_lineups(event) + '\n\n'
        body += '___\n'
        body += _get_key_event_text(event) + '\n\n'
    body += '___\n'
    body += _get_bot_footer() + '\n\n'
    return body
