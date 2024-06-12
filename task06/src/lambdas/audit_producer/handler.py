from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import uuid
from datetime import datetime
import os
import boto3

_LOG = get_logger('AuditProducer-handler')

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('table_name', "")
table = dynamodb.Table(table_name)

        
class AuditProducer(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        for record in event.get('Records', tuple()):
            if record['eventName'] == 'INSERT':
                self.handle_insert(record)
            elif record['eventName'] == 'MODIFY':
                self.handle_modify(record)
        return 200
    

    def handle_insert(self, record):
        new_image = record['dynamodb']['NewImage']
        key = new_image['key']['S']
        value = new_image['value']['S']
        
        audit_item = {
            'id': str(uuid.uuid4()),
            'itemKey': key,
            'modificationTime': datetime.utcnow().isoformat(),
            'newValue': {
                'key': key,
                'value': value
            }
        }
        
        table.put_item(Item=audit_item)

    def handle_modify(self, record):
        new_image = record['dynamodb']['NewImage']
        old_image = record['dynamodb']['OldImage']
        key = new_image['key']['S']
        new_value = new_image['value']['S']
        old_value = old_image['value']['S']
        
        audit_item = {
            'id': str(uuid.uuid4()),
            'itemKey': key,
            'modificationTime': datetime.utcnow().isoformat(),
            'updatedAttribute': 'value',
            'oldValue': old_value,
            'newValue': new_value
        }
        
        table.put_item(Item=audit_item)
    

HANDLER = AuditProducer()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
