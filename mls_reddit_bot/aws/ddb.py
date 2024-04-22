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
            self.game_completed_field: {
                'BOOL': False,
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


    def _update_field(
            self,
            key: str,
            val: str,
            valtype: str = 'S'
        ) -> bool:
        """
        Update a field.
        On success, returns True and updates self.item.
        On failure, returns False.
        """
        try:
            response = DDB.update_item(
                TableName=self.table_name,
                Key=self.key,
                UpdateExpression=f'SET {key} = :val',
                ExpressionAttributeValues={
                    ':val': {
                        valtype: val,
                    },
                },
                ReturnValues='ALL_NEW', # returns entire item
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.item = response['Attributes']
                return True
        except Exception as e:
            log.exception(f'failed to update ddb table {key}={val}')
            return False


    def update_reddit_thread_id(self, submission_id):
        if self.get_reddit_thread_id() == submission_id:
            return True # already set, skip duplicate
        return self._update_field(self.reddit_thread_id_field, submission_id)


    def get_reddit_thread_id(self):
        return self.item.get(self.reddit_thread_id_field, {}).get('S', None)


    def set_game_completed(self, completed: str = True):
        submission_id = self.get_reddit_thread_id()
        if not submission_id:
            log.error(f'refusing to issue game completion put, no reddit thread')
            return False
        return self._update_field(self.game_completed_field, completed, 'BOOL')


    def is_game_completed(self):
        return self.item.get(self.game_completed_field, {}).get('BOOL', False)



if __name__ == '__main__':
    class DummyEvent:
        def __init__(self, id):
            self.id = id
            self.date_str = '2025-01-01'

    for match_id in [
            DummyEvent('fake-1'),
            DummyEvent('fake-2'),
        ]:
        g = DdbGameThread(match_id)
        rti = g.get_reddit_thread_id()
        if rti:
            g._update_field('match_date', '2026-12-12')
            g.update_reddit_thread_id('testing-value')
            g.set_game_completed(False)
            print(f'reddit thread id for match {match_id} is {rti}')
        else:
            rti = 'some-reddit-id' # reddit.create_submission(...)
            g.update_reddit_thread_id(rti)
