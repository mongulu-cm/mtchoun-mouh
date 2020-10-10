from registre import get_RegisterName
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from  config import Table_Users, Table_Registers

def Scan_Users(UserName,Table_Users):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(Table_Users)
    response = table.scan(
        FilterExpression=Attr('UserName').eq(UserName)
    )
    return response['Items']

def amazone_ses_mail(RECIPIENT):
    SENDER = "Sender Name <tagnefabiola97@gmail.com>"
    AWS_REGION = "us-east-1"
    SUBJECT = "Passeport disponible"
    BODY_TEXT = ("Votre passeport est sortie  (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )
    BODY_HTML = """<html>
          <head>Bonjour, </head>
                <body>
                  
                  <p> 
                    
                   Votre passeport  est disponible au consulat de Marseille.<br>
                   N'oubliez pas de vous munir de votre reçu de dépot. <br>
                   Retrait  des documents etablis du lundi au vendredi de 15H30 à 16H00 (selon l'affluence).<br> <br> <br>
                   Cordialement, 
                   
                </p>
                </body>
                </html>
                            """         
                            
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
    
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def Delete_Backup(D_Name):
    primary_column_Name='Name'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(Table_Registers)
    response = table.delete_item(
        Key={
            primary_column_Name:D_Name
        }
    )

Index_Register=get_RegisterName()
for i in Index_Register:
    print(i)
    Name=i[0]
    Email=i[1]
    Scan_reponse=Scan_Users(Name,Table_Users)  
    if len(Scan_reponse)==0:
      print(" votre passeport n'est pas sorti")
    else:
        amazone_ses_mail(Email)
        Delete_Backup(Name)
