import boto3

def Delete_Backup(D_Name):
    primary_column_Name='Name'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Register')
    response = table.delete_item(
        Key={
            primary_column_Name:D_Name
        }
    )
Delete_Backup('TAGNE TCHANA FABIOLA CORINNE')