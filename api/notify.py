from registre import get_RegisterName
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

# from config import Table_Registers,maintainer_mail
import os


def Scan_Users(UserName, Table_Users):
    """
    Scan the table for the user name and return the items

    :param UserName: The user name of the user you want to scan for
    :param Table_Users: The name of the DynamoDB table that contains the user information
    :return: A list of dictionaries.
    """
    region = os.environ["REGION"]
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(Table_Users)
    response = table.scan(FilterExpression=Attr("UserName").eq(UserName))
    return response["Items"]


def amazone_ses_mail(NAME, RECIPIENT, URL_IMAGE, maintainer=False):
    """
    It sends an email to the recipient with the image attached

    :param NAME: The name of the person to whom the email is being sent
    :param RECIPIENT: The email address of the recipient
    :param URL_IMAGE: The URL of the image to be sent in the email
    :param maintainer: if True, send an email to the maintainer of the project, defaults to False (optional)
    """
    maintainer_mail = os.environ["MAINTAINER_MAIL"]
    NAME = NAME.upper()
    SENDER = f"Collectif mongulu <{maintainer_mail}>"
    AWS_REGION = "eu-central-1"

    if not maintainer:

        SUBJECT = "Ton passeport est disponible"
        BODY_TEXT = (
            "Votre passeport est sortie  (Python)\r\n"
            "This email was sent with Amazon SES using the "
            "AWS SDK for Python (Boto)."
        )
        BODY_HTML = """<html>
              <head> <p >Hello {NAME} ,</p></head>
                    <body>

                      <p>

                       Nous sommes heureux de t'annoncer de que ton <strong>passeport  est disponible au consulat de Marseille</strong> &#128578; .<br>

                       Tu peux dès à présent t'y rendre <strong>muni de votre reçu de dépot et votre ancien passeport.</strong> <br>
                       Retrait  des documents etablis du lundi au vendredi de 15H30 à 16H00 (selon l'affluence).<br> <br> <br>

                       Tu veux voir pour croire ? <br>
                       On a prévu ça  &#128521;, suis juste ce lien: :  {URL_IMAGE} .<br>

                       <p style="font-size:16px">On fait comme ça, On est ensemble. </p>
                       <p> Un soucis ? Il vous suffit de faire répondre à ce mail </a>  </p>

                    </p>
                    </body>
                    </html>
                                """.format(
            URL_IMAGE=URL_IMAGE, NAME=NAME
        )
    else:
        # maintainer
        SUBJECT = "Nouvelles images détectés sur le site du consulat"
        BODY_TEXT = f"Lien vers la première image: {URL_IMAGE}"
        BODY_HTML = (
            """<html> Lien vers la première image: {URL_IMAGE} </html>""".format(
                URL_IMAGE=URL_IMAGE
            )
        )

    CHARSET = "UTF-8"
    client = boto3.client("ses", region_name=AWS_REGION)
    try:

        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])

def amazone_ses_mail_registration(NAME, RECIPIENT):
    """
    It sends an registration confirmation  email to the recipient

    :param NAME: The name of the person to whom the email is being sent
    :param RECIPIENT: The email address of the recipient
    
    """
    maintainer_mail = os.environ["MAINTAINER_MAIL"]
    NAME = NAME.upper()
    SENDER = f"Collectif mongulu <{maintainer_mail}>"
    
    s3 = boto3.resource("s3")
    obj = s3.Object('templates-emails','mtchoun-mouh registration.html')
    #TODO REPLACE replace with format 
    data=str(obj.get()['Body'].read().decode('utf-8') ).strip().replace("\\n","").replace("{name}!", NAME)
            
    AWS_REGION = "eu-central-1"


    SUBJECT = "Confirmation d'enregistrement"
    BODY_TEXT = (
        "Confirmation d'enregistrement\r\n"
        "This email was sent with Amazon SES using the "
        "AWS SDK for Python (Boto)."
    )
    BODY_HTML = data

    CHARSET = "UTF-8"
    client = boto3.client("ses", region_name=AWS_REGION)
    try:

        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])

def Delete_Backup(D_Name):
    """
    It deletes the backup from the DynamoDB table

    :param D_Name: The name of the backup you want to delete
    """
    Table_Registers = os.environ["REGISTERS_TABLE"]
    primary_column_Name = "Name"
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Registers)
    response = table.delete_item(Key={primary_column_Name: D_Name})


def notify_user_registered():
    """
    It scans the DynamoDB table for the user's name, and if it finds it, it sends an email to the user with the URL of the
    image
    """
    Table_Users = os.environ["USERS_TABLE"]
    Index_Register = get_RegisterName()
    for i in Index_Register:
        # print(i)
        Name = i[0]
        Email = i[1]
        Scan_reponse = Scan_Users(Name, Table_Users)
        if len(Scan_reponse) == 0:
            print(Name + " votre passeport n'est pas sorti")
        else:
            amazone_ses_mail(Name, Email, Scan_reponse[0]["URLImage"])
            Delete_Backup(Name)


if __name__ == "__main__":
    notify_user_registered()
