from tests.test_hello_world import HelloWorldLambdaTestCase


class TestSuccess(HelloWorldLambdaTestCase):

    def test_success(self):
        response = {
            "statusCode": 200,
            "message": "Hello from Lambda",
        }
        self.assertEqual(self.HANDLER.handle_request(dict(), dict()), response)

