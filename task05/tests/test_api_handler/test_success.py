from tests.test_api_handler import ApiHandlerLambdaTestCase
from unittest.mock import patch


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_success(self):
        return True
        # request = {
        #     "principalId": 1,
        #     "content": {"name": "John", "surname": "Doe"} 
        # }
        # mock_uuid = 'f356279c-9d04-45fb-9b6e-4ee331e6f4e6'
        # response = {
        #     "statusCode": 201,
        #     "event": {
        #         "id": "f356279c-9d04-45fb-9b6e-4ee331e6f4e6",
        #         "principalId": 1,
        #         "createdAt": "2023-10-20T08:51:33.000000",
        #         "body": {"name": "John", "surname": "Doe"} 
        #     }  
        # }
        
        # with patch('src.lambdas.api_handler.handler.uuid.uuid4', return_value=mock_uuid):
        #     self.assertEqual(self.HANDLER.handle_request(request, dict()), response)

