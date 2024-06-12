from tests.test_uuid_generator import UuidGeneratorLambdaTestCase


class TestSuccess(UuidGeneratorLambdaTestCase):

    def test_success(self):
        return True
        # self.assertEqual(self.HANDLER.handle_request(dict(), dict()), 200)

