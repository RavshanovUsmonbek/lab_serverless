from tests.test_sqs_handler import SqsHandlerLambdaTestCase


class TestSuccess(SqsHandlerLambdaTestCase):

    def test_success(self):
        event = {
            "Records": [
                {
                "messageId": "1a2b3c4d-5678-90ab-cdef-12345EXAMPLE",
                "receiptHandle": "AQEBwJnKp...Mg==",
                "body": "{\"key1\": \"value1\", \"key2\": \"value2\"}",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1573251510774",
                    "SenderId": "AIDAIEXAMPLE",
                    "ApproximateFirstReceiveTimestamp": "1573251510774"
                },
                "messageAttributes": {},
                "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-west-2:123456789012:MyQueue",
                "awsRegion": "us-west-2"
                }
            ]
        }
        self.assertEqual(self.HANDLER.handle_request(event, dict()), 200)

