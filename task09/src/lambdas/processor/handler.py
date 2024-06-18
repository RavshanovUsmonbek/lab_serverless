from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json
from lambdas.layers.openmeteo.openmeteo import OpenMeteoClient
import boto3
import os
import uuid
from botocore.exceptions import ClientError
from decimal import Decimal


_LOG = get_logger('Processor-handler')

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('table_name', "")
table = dynamodb.Table(table_name)


class Processor(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        response = OpenMeteoClient().get_data()
        forecast = data = json.loads(response.text, parse_float=Decimal)
        data = {
            'id': str(uuid.uuid4()),  # Generate a unique UUID
            "forecast": {
                "elevation": forecast['elevation'],
                "generationtime_ms": forecast['generationtime_ms'],
                "hourly": {
                    "temperature_2m": forecast['hourly']['temperature_2m'],
                    "time": forecast['hourly']['time']
                },
                "hourly_units": {
                    "temperature_2m": forecast['hourly_units']['temperature_2m'],
                    "time": forecast['hourly_units']['time']
                },
                "latitude": forecast['latitude'],
                "longitude": forecast['longitude'],
                "timezone": forecast['timezone'],
                "timezone_abbreviation": forecast['timezone_abbreviation'],
                "utc_offset_seconds": forecast['utc_offset_seconds']
            }
        }
        try:
            # Put the item into the table
            response = table.put_item(Item=data)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Successfully inserted item!', 'id': data['id']})
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Error inserting item: {e.response['Error']['Message']}")
            }
    

HANDLER = Processor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
