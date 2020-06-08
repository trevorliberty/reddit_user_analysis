from .Model import Model
import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal, localcontext
from src.controllers.processUser import User
import math


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
        :returns: None if the user is not found in the database. User object if it is.
        :raises: Databse errors on connection and insertion
        """

        try:
            u = self.table.get_item(
                Key={
                    'username': userName
                }
            )['Item']

            return({
                'name': u['username'],
                'karma': u['karma'],
                'lowestRatedComment': u['lowestRatedComment'],
                'languageComplexity' : u['languageComplexity'],
                'topRatedComment': u['topRatedComment'],
                'sentimentRatios': u['sentimentRatios'],
                'topSubreddits': u['topSubreddits'],
                'sentimentChangeRatios': u['sentimentChangeRatios'],
                'dominantSentiment': u['dominantSentiment']
            })
        except Exception as e:
            print(e)
            return False

    def insertUser(self, user: User):
        """
        Inserts proccessed user information into the database for future access.
        :param user: user object with proccessed fields
        :returns: nothing
        :raises: Databse errors on connection and insertion
        """

        sentimentRatios = vars(user.sentimentRatios)
        sentimentRatios = {k: Decimal(str(v))
                           for k, v in sentimentRatios.items()}

        sentimentChangeRatios = vars(user.sentimentChangeRatios)
        sentimentChangeRatios = {k: Decimal(
            str(v)) for k, v in sentimentChangeRatios.items()}

        topSubreddits = {}

        for i in user.topSubreddits:
            topSubreddits.update(i)

        topSubreddits = {k: Decimal(
            str(v)) for k, v in topSubreddits.items()}

        lowestRated = {
            'contents': user.lowestRatedComment.contents,
            'score': user.lowestRatedComment.score,
            'subreddit': user.lowestRatedComment.subreddit,
            'sentiment': user.lowestRatedComment.sentiment,
        }

        topRated = {
            'contents': user.topRatedComment.contents,
            'score': user.topRatedComment.score,
            'subreddit': user.topRatedComment.subreddit,
            'sentiment': user.topRatedComment.sentiment,
        }

        userToInsert = {
            'username': user.name,
            'language': user.language,
            'languageComplexity': Decimal(str(user.languageComplexity)),
            'karma': user.karma,
            'topSubreddits': topSubreddits,
            'dominantSentiment': user.dominantSentiment,
            'lowestRatedComment': lowestRated,
            'topRatedComment': topRated,
            'sentimentChangeRatios': sentimentChangeRatios,
            'sentimentRatios': sentimentRatios
        }

        self.table.put_item(Item=userToInsert)
