from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import json

log = get_logger('HelloWorld-handler')


class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        path = event.get('rawPath', '')
        method = event.get('requestContext', {}).get('http', {}).get("method")

        error_body = {
            "statusCode": 400,
            "message": f"Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}"
        }
        if path != "/hello" or method != "GET":
            return {
                "statusCode": 400,
                "body": json.dumps(error_body)
            }

        body = {
            "statusCode": 200,
            "message": "Hello from Lambda",
        }
        return {
            "statusCode": 200,
            "body": json.dumps(body)
        }


HANDLER = HelloWorld()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
