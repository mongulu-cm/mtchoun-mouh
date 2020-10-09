import boto3
import subprocess
from sys import argv
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
from  config import Table_Registers



def  insert_dynamodb_registered(U_Name,E_Mail):
    dynamodb = boto3.resource('dynamodb')
    table =dynamodb.Table(Table_Registers)
    table.put_item(
        Item={
            'Name':U_Name.lower(),
            'EMail':E_Mail
            }
    )
    
def get_RegisterName():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(Table_Registers)
    response = table.scan()
    lst = []
    for i in response['Items']:
        lst.append([ i['Name'],i['EMail'] ])
    #print(lst)
    return lst 


    
def verifying_Register_mail(E_Mail):
    subprocess.run(["aws","ses","verify-email-identity","--email-address", E_Mail])


if __name__ == "__main__":
    insert_dynamodb_registered(argv[1],argv[2])
    verifying_Register_mail(argv[2])

    
    

    
