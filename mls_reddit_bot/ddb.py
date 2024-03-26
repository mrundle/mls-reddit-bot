#!/usr/bin/env python3
import boto3
import json

from mls_reddit_bot import log

DDB = boto3.client('dynamodb')

class DdbGameThread(object):
    def __init__(self, mls_game_id):
        self.table_name = 'mls-matches'
        self.reddit_thread_id_field = 'reddit_submission_id'
        self.mls_game_id = mls_game_id
        self.key = {
            'id': {
                'S': str(self.mls_game_id),
            }
        }
        self.item, self.error = self.fetch()

    def fetch(self):
        response = DDB.get_item(
            TableName=self.table_name,
            Key=self.key,
        )
        md = {}
        code = -1
        try:
            md = response['ResponseMetadata']
            code = md['HTTPStatusCode']
            success = str(code) == "200"
        except:
            log.error(f'ddb: failure (code={code}) fetching from table {self.table_name}, key={key}')
            success = False

        return (
            response.get('Item', {}),
            not success,
        )

    def needs_creation(self):
        return not self.item and not self.error

    def create(self):
        if self.error:
            log.error('ddb: refusing to recreate after fetch error')
            return False
        response = DDB.put_item(
            TableName=self.table_name,
            Item=self.key,
        )
        md = {}
        code = -1
        try:
            md = response['ResponseMetadata']
            code = md['HTTPStatusCode']
            success = str(code) == "200"
            log.debug(f'ddb: created entry for key={self.key}')
        except Exception as e:
            log.error(f'ddb: failure (code={code}) putting to table '
                      f'{self.table_name}, key={self.key}')
            success = False

        if success:
            self.item = self.key

        return success

    def update_reddit_thread_id(self, submission_id):
        if self.get_reddit_thread_id() == submission_id:
            return True # already set, skip duplicate

        item = {
            'id': {
                'S': str(self.mls_game_id),
            },
            self.reddit_thread_id_field: {
                'S': str(submission_id),
            },
        }
        response = DDB.put_item(
            TableName=self.table_name,
            Item=item,
        )
        try:
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.item = item
                log.debug(f'ddb: set reddit submission id to {submission_id} '
                          f'for match id {self.mls_game_id}')
                return True
        except:
            log.error(f'ddb: failed to set reddit submission id to '
                      f'{submission_id} for match id {self.mls_game_id}')
            return False

    def get_reddit_thread_id(self):
        return self.item.get(self.reddit_thread_id_field, {}).get('S', None)


if __name__ == '__main__':
    for match_id in [
            'fake-1',
            'fake-2',
        ]:
        g = DdbGameThread(match_id)
        rti = g.get_reddit_thread_id()
        if rti:
            print(f'reddit thread id for match {match_id} is {rti}')
        else:
            rti = 'some-reddit-id' # reddit.create_submission(...)
            g.update_reddit_thread_id(rti)
