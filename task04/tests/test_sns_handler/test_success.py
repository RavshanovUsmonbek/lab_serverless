from tests.test_sns_handler import SnsHandlerLambdaTestCase


class TestSuccess(SnsHandlerLambdaTestCase):

    def test_success(self):
        event = {
            "Records": [
                {
                    "EventSource": "aws:sns",
                    "Sns": {
                        "Type": "Notification",
                        "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                        "TopicArn": "arn:aws:sns:us-east-1:123456789012:ExampleTopic",
                        "Subject": "example subject",
                        "Message": "{\"key1\":\"value1\",\"key2\":\"value2\"}",
                    }
                }
            ]
        }

        self.assertEqual(self.HANDLER.handle_request(event, dict()), 200)

