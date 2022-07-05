import boto3
import subprocess
import os
from sys import argv
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr


def insert_dynamodb_registered(U_Name, E_Mail):
    Table_Registers = os.environ["REGISTERS_TABLE"]
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Registers)
    table.put_item(Item={"Name": U_Name.lower(), "EMail": E_Mail})


def get_RegisterName():
    Table_Registers = os.environ["REGISTERS_TABLE"]
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Registers)
    response = table.scan()
    # print(lst)
    return [[i["Name"], i["EMail"]] for i in response["Items"]]


def verifying_Register_mail(E_Mail):
    client = boto3.client("ses")
    client.verify_email_identity(EmailAddress=E_Mail)


if __name__ == "__main__":
    insert_dynamodb_registered(argv[1], argv[2])
    verifying_Register_mail(argv[2])
