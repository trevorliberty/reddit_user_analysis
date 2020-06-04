from src.Model import Model
import boto3
import json
from boto3.dynamodb.conditions import Key


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class Users(Model):
    """
    AWS DynamoDB table
    """

    def __init__(self):
        self.resource = boto3.resource("dynamodb", region_name='us-east-1')
        self.table = self.resource.Table('users')
        try:
            self.table.load()
        except Exception as e:
            self.resource.create_table(
                TableName='users',
                KeySchema=[
                    {
                        "AttributeName": 'username',
                        "KeyType": 'HASH',
                    },
                ],
                AttributeDefinitions=[
                    {
                        "AttributeName": 'username',
                        "AttributeType": 'S',
                    },
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1
                }
            )

    def getUser(self, userName):
        """
        Retrieves the user from database.
        :param userName: name of the user to be retrieved
        :returns: undefined if the user is not found in the database. User object if it is.
        :raises: Databse errors on connection and insertion
        """

        u = self.table.get_item(
            TableName='users',
            Key={
                'string': {
                    'S': userName
                }
            }
        )['Item']

        if(u is not None):
            return({
                'name': u['name'],
                'karma': u['karma'],
                'lowestRatedComment': u['lowestRatedComment'],
                'topRatedComment': u['topRatedComment'],
                'sentimentAverage': u['sentimentAverage'],
                'sentimentHighestComment': u['sentimentHighestComment'],
                'sentimentLowestComment': u['sentimentLowestComment'],
                'sentimentRatios': u['sentimentRatios'],
                'topSubreddits': u['topSubreddits']
            })

    def insertUser(self, user):
        """
        Inserts proccessed user information into the database for future access.
        :param user: user object with proccessed fields
        :returns: nothing
        :raises: Databse errors on connection and insertion
        """

        userToInsert = {
            'name': user.name,
            'karma': user.karma,
            'lowestRatedComment': user.lowestRatedComment,
            'topRatedComment': user.topRatedComment,
            'sentimentAverage': user.sentimentAverage,
            'sentimentHighestComment': user.sentimentHighestComment,
            'sentimentLowestComment': user.sentimentLowestComment,
            'sentimentRatios': user.sentimentRatios,
            'topSubreddits': user.topSubreddits,

        }

        self.table.put_item(Item=userToInsert)