import os
import json
import boto3
import uuid
from time import sleep
import re
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
from pydantic import ValidationError, BaseModel, EmailStr, constr, validator
from typing import Optional
from functools import wraps


_LOG = get_logger('ApiHandler-handler')

cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

tables_table = os.environ.get('tables_table', "")
reservation_table = os.environ.get('reservation_table', "")
tables_table = dynamodb.Table(tables_table)
reservations_table = dynamodb.Table(reservation_table)


class UserPoolNotFoundException(Exception):
    pass


class UserPoolClientNotFoundException(Exception):
    pass


class SignUpModel(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str

    @validator('password')
    def password_complexity(cls, value):
        import re
        if not re.match(r'^[a-zA-Z0-9$%^*-_]+$', value):
            raise ValueError('Password must be alphanumeric and can include only "$%^*_-".')
        
        return value
    

class SigninModel(BaseModel):
    email: EmailStr
    password: constr(min_length=12, regex=r'^[a-zA-Z0-9$%^*]+$')

    @validator('password')
    def password_complexity(cls, value):
        import re
        if not re.match(r'^[a-zA-Z0-9$%^*]+$', value):
            raise ValueError('Password must be alphanumeric and can include only "$%^*".')
        return value


class TableModel(BaseModel):
    id: int
    number: int
    places: int
    isVip: bool
    minOrder: Optional[int]

    @staticmethod
    def from_dynamodb(item):
        return TableModel(
            id=int(item['id']),
            number=int(item['number']),
            places=int(item['places']),
            isVip=bool(item['isVip']),
            minOrder=int(item['minOrder']) if 'minOrder' in item else None
        )


class TablesListModel(BaseModel):
    tables: list[TableModel]
    

class ReservationModel(BaseModel):
    tableNumber: int
    clientName: str
    phoneNumber: str
    date: constr(regex=r'^\d{4}-\d{2}-\d{2}$')
    slotTimeStart: constr(regex=r'^\d{2}:\d{2}$')
    slotTimeEnd: constr(regex=r'^\d{2}:\d{2}$')
    
    @validator('phoneNumber')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?\d{10,15}$', v):
            raise ValueError('Invalid phone number')
        return v
    

class UserPoolData:
    def __init__(self, cognito_client):
        booking_userpool = os.environ.get('booking_userpool')
        self._pool_id = self.get_user_pool_id_by_name(cognito_client, booking_userpool)
        self._client_id = self.get_client_id_by_name(cognito_client, self._pool_id) 
    
    def _paginate(self, method, key, **kwargs):
        """Generator to paginate through AWS API responses."""
        while True:
            response = method(**kwargs)
            yield from response[key]
            if 'NextToken' not in response:
                break
            kwargs['NextToken'] = response['NextToken']

    def get_data(self):
        return self._pool_id, self._client_id

    def get_user_pool_id_by_name(self, cognito_client, user_pool_name):
        for pool in self._paginate(cognito_client.list_user_pools, 'UserPools', MaxResults=60):
            if pool['Name'] == user_pool_name:
                return pool['Id']
        raise UserPoolNotFoundException(f"User pool '{user_pool_name}' not found.")


    def get_client_id_by_name(self, cognito_client, user_pool_id, client_name="client-app"):
        for client in self._paginate(cognito_client.list_user_pool_clients, 'UserPoolClients', UserPoolId=user_pool_id, MaxResults=60):
            if client['ClientName'] == client_name:
                return client['ClientId']
        raise UserPoolClientNotFoundException(f"Client '{client_name}' not found in user pool '{user_pool_id}'.")


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
            
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        path = event['path']
        method = event['httpMethod']
        
        if path == '/signup' and method == 'POST':
            return self.signup(event)
        elif path == '/signin' and method == 'POST':
            return self.signin(event)
        elif path == '/tables' and method == 'GET':
            return self.get_tables(event)
        elif path == '/tables' and method == 'POST':
            return self.create_table(event)
        elif path.startswith('/tables/') and method == 'GET':
            return self.get_table(event)
        elif path == '/reservations' and method == 'POST':
            return self.create_reservation(event)
        elif path == '/reservations' and method == 'GET':
            return self.get_reservations(event)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid path or method'})
            }

    def signup(self, event):
        self._pool_id, self._client_id = UserPoolData(cognito).get_data()
        try:
            payload = json.loads(event['body'])
            body = SignUpModel(**payload)
        except ValidationError as e:
            _LOG.error(f"ERROR On validation: {payload}")
            return {
                'statusCode': 400,
                'body': e.json()
            }
            
        try:
            cognito.sign_up(
                ClientId=self._client_id,
                Username=body.email,
                Password=body.password,
                UserAttributes=[
                    {'Name': 'given_name', 'Value': body.firstName},
                    {'Name': 'family_name', 'Value': body.lastName},
                    {'Name': 'email', 'Value': body.email},
                ]
            )
            
            #Confirm the user immediately to bypass NEW_PASSWORD_REQUIRED
            cognito.admin_confirm_sign_up(
                UserPoolId=self._pool_id,
                Username=body.email
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User created successfully'})
            }
        except cognito.exceptions.UsernameExistsException:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'User already exists'})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def signin(self, event):
        self._pool_id, self._client_id = UserPoolData(cognito).get_data()
        try:
            body = SigninModel(**json.loads(event['body']))
        except ValidationError as e:
            return {
                'statusCode': 400,
                'body': e.json()
            }

        try:
            response = cognito.admin_initiate_auth(
                UserPoolId=self._pool_id,
                ClientId=self._client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': body.email,
                    'PASSWORD': body.password
                }
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'accessToken': response['AuthenticationResult']['IdToken']})
            }
        except cognito.exceptions.NotAuthorizedException:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def create_table(self, event):
        try:
            body = TableModel(**json.loads(event['body']))
        except ValidationError as e:
            return {
                'statusCode': 400,
                'body': e.json()
            }

        item = body.dict()
        
        try:
            tables_table.put_item(Item=item)
            return {
                'statusCode': 200,
                'body': json.dumps({'id': item['id']})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def get_table(self, event):
        table_id = int(event['pathParameters']['tableId'])
        try:
            response = tables_table.get_item(Key={'id': table_id})
            if 'Item' in response:
                return {
                    'statusCode': 200,
                    'body': json.dumps(TableModel(**response['Item']).dict())
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Table not found'})
                }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def create_reservation(self, event):
        try:
            body = ReservationModel(**json.loads(event['body']))
        except ValidationError as e:
            return {
                'statusCode': 400,
                'body': e.json()
            }

        reservation_id = str(uuid.uuid4())
        item = body.dict()
        item['id'] = reservation_id

        try:
            reservations_table.put_item(Item=item)
            return {
                'statusCode': 200,
                'body': json.dumps({'reservationId': reservation_id})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def get_reservations(self, event):
        try:
            response = reservations_table.scan()
            reservations = [ReservationModel(**item).dict() for item in response['Items']]
            return {
                'statusCode': 200,
                'body': json.dumps({'reservations': reservations})
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    def get_tables(self, event):
        try:
            response = tables_table.scan()
            items = response.get('Items', [])
            # Convert DynamoDB items to TableItem instances
            tables = [TableModel.from_dynamodb(item) for item in items]
            response_model = TablesListModel(tables=tables)
            return {
                'statusCode': 200,
                'body': json.dumps(response_model.dict())
            }
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }
    

HANDLER = ApiHandler()

def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
