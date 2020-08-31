import boto3
from boto3.dynamodb.conditions import Key


def query_Users(UserNama):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.query(
        KeyConditionExpression=Key('UserName').eq(UserName)
    )
    return response['Items']
