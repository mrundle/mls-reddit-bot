import boto3
import json

from mls_reddit_bot import constants
from mls_reddit_bot import log

DDB = boto3.client('dynamodb')

class DdbGameThread(object):
    def __init__(self, event):
        self.table_name = constants.AWS_DDB_TABLE_NAME
        self.match_date_id_field = 'match_date'
        self.reddit_thread_id_field = 'reddit_submission_id'
        self.game_completed_field = 'game_completed'
        self.event = event
        self.event_id = event.id
        self.key = {
            'id': {
                'S': str(self.event_id),
            },
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
        item = {
            'id': {
                'S': str(self.event_id),
            },
            self.match_date_id_field: {
                'S': self.event.date_str,
            },
        }
        response = DDB.put_item(
            TableName=self.table_name,
            Item=item,
        )
        md = {}
        code = -1
        try:
            md = response['ResponseMetadata']
            code = md['HTTPStatusCode']
            success = str(code) == "200"
        except Exception as e:
            log.error(f'ddb: failure (code={code}) putting to table '
                      f'{self.table_name}, key={self.key})')
            success = False

        if success:
            self.item = self.key

        return success

    def update_reddit_thread_id(self, submission_id):
        if self.get_reddit_thread_id() == submission_id:
            return True # already set, skip duplicate

        item = {
            'id': {
                'S': str(self.event_id),
            },
            self.reddit_thread_id_field: {
                'S': str(submission_id),
            },
            self.match_date_id_field: {
                'S': self.event.date_str,
            },
        }
        response = DDB.put_item(
            TableName=self.table_name,
            Item=item,
        )
        try:
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.item = item
                return True
        except:
            log.error(f'ddb: failed to set reddit submission id to '
                      f'{submission_id} for match id {self.event_id}')
            return False

    def get_reddit_thread_id(self):
        return self.item.get(self.reddit_thread_id_field, {}).get('S', None)

    def set_game_completed(self):
        submission_id = self.get_reddit_thread_id()
        if not submission_id:
            log.error(f'refusing to issue game completion put, no reddit thread')
            return False
        # TODO merge with other put_item logic
        item = {
            'id': {
                'S': str(self.event_id),
            },
            self.reddit_thread_id_field: {
                'S': str(submission_id),
            },
            self.game_completed_field: {
                'BOOL': True,
            }
        }
        response = DDB.put_item(
            TableName=self.table_name,
            Item=item,
        )
        try:
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.item = item
                return True
        except:
            log.error(f'ddb: failed to set {self.game_completed_field}=True '
                      f'for match id {self.event_id}')
            return False

    def is_game_completed(self):
        return self.item.get(self.game_completed_field, {}).get('BOOL', False)


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
