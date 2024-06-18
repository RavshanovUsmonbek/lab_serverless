from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
from lambdas.layers.openmeteo.openmeteo import OpenMeteoClient
import json

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        data = OpenMeteoClient().get_data()
    
        path = event.get('rawPath', '')
        method = event.get('requestContext', {}).get('http', {}).get("method")

        error_body = {
            "statusCode": 400,
            "message": f"Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}"
        }
        if path != "/weather" or method != "GET":
            return {
                "statusCode": 400,
                "body": json.dumps(error_body)
            }
        return {
            "statusCode": 200,
            "body": json.dumps(data)
        }
        return response
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
