from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
from lambdas.layers.openmeteo.openmeteo import OpenMeteoClient

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        response = OpenMeteoClient().get_data()
        return response
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
