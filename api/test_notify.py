import boto3
from moto import mock_dynamodb
from notify import Scan_Users
import os
import pytest
from extract import insert_dynamodb


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("REGION", "eu-central-1")
    monkeypatch.setenv("USERS_TABLE", "Users")
    monkeypatch.setenv("REGISTERS_TABLE", "Register")


@mock_dynamodb
def test_scan_users():
    Table_Users = os.environ["USERS_TABLE"]
    dynamodb = boto3.client("dynamodb", region_name="eu-central-1")
    dynamodb.create_table(
        AttributeDefinitions=[
            {"AttributeName": "UserName", "AttributeType": "S"},
        ],
        TableName=Table_Users,
        KeySchema=[
            {"AttributeName": "UserName", "KeyType": "HASH"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 123, "WriteCapacityUnits": 123},
    )
    assert Scan_Users("fabiola", Table_Users) == []

    insert_dynamodb("fabiola", "fabiolaImage")
    assert len(Scan_Users("fabiola", Table_Users)) == 1
