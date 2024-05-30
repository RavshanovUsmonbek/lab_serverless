import unittest
from tests.test_hello_world import HelloWorldLambdaTestCase
import json


class TestSuccess(HelloWorldLambdaTestCase):

    def test_success(self):
        event = {
            "rawPath": "/hello",
            "requestContext": {
                "http": {
                    "method": "GET",
                }
            }
        }

        response = {
            "statusCode": 200,
            "body": json.dumps({
                "statusCode": 200,
                "message": "Hello from Lambda",
            })
        }
        self.assertEqual(self.HANDLER.handle_request(event, dict()), response)

    def test_failure(self):
        event = {
            "rawPath": "/other",
            "requestContext": {
                "http": {
                    "method": "PUT",
                }
            }
        }
        response = {
            "statusCode": 400,
            "body": json.dumps({
                "statusCode": 400,
                "message": "Bad request syntax or unsupported method. Request path: /other. HTTP method: PUT"
            })
        }

        self.assertEqual(self.HANDLER.handle_request(event, dict()), response)


if __name__ == '__main__':
    # Running tests with output buffering disabled
    unittest.main(buffer=False)
