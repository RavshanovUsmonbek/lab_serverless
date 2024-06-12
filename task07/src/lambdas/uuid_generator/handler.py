from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import boto3
import uuid
import json
from datetime import datetime
import os

_LOG = get_logger('UuidGenerator-handler')


# Initialize S3 client
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get("target_bucket", "")


class UuidGenerator(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # Get the current time in ISO 8601 format
        execution_time = datetime.now().isoformat() + 'Z'
        
        # Generate 10 random UUIDs
        uuid_list = [str(uuid.uuid4()) for _ in range(10)]
        
        # Prepare the data to be written to the S3 bucket
        data = {
            'ids': uuid_list
        }
        
        # Define the file name based on the execution start time
        file_name = execution_time
        
        # Write the data to the S3 bucket
        try:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully created file {file_name} with UUIDs.')
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: {str(e)}')
            }
        

HANDLER = UuidGenerator()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
