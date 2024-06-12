from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import boto3
from datetime import datetime
import uuid

_LOG = get_logger('ApiHandler-handler')

dynamodb = boto3.resource('dynamodb')
table_name = 'cmtr-5c54baa5-Events'
table = dynamodb.Table(table_name)

class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # Extract principalId and content from the request
        principal_id = event['principalId']
        content = event['content']

        # Generate a unique ID for the item
        item_id = str(uuid.uuid4())
        
        # Get the current timestamp
        created_at = datetime.now().isoformat()

        # Create the item to be saved in DynamoDB
        item = {
            'id': item_id,
            'principalId': principal_id,
            'createdAt': created_at,
            'body': content
        }

        # Save the item to DynamoDB
        table.put_item(Item=item)

        # Create the response object
        response = {
            'statusCode': 201,
            'event': item
        }
        return response
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
