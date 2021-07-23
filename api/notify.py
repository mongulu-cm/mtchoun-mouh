from registre import get_RegisterName
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from config import Table_Users, Table_Registers,maintainer_mail


def Scan_Users(UserName, Table_Users):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(Table_Users)
    response = table.scan(
        FilterExpression=Attr('UserName').eq(UserName)
    )
    return response['Items']


def amazone_ses_mail(NAME, RECIPIENT, URL_IMAGE,maintainer=False):
    NAME = NAME.upper()
    SENDER = f"Collectif mongulu <{maintainer_mail}>"
    AWS_REGION = "eu-central-1"

    if not maintainer:

        SUBJECT = "Ton passeport est disponible"
        BODY_TEXT = ("Votre passeport est sortie  (Python)\r\n"
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
                                """.format(URL_IMAGE=URL_IMAGE, NAME=NAME)
    else:
        # maintainer
        SUBJECT = "Nouvelles images détectés sur le site du consulat"
        BODY_TEXT = f"Lien vers la première image: {URL_IMAGE}"
        BODY_HTML = """<html> Lien vers la première image: {URL_IMAGE} </html>""".format(URL_IMAGE=URL_IMAGE)

    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)
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
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def Delete_Backup(D_Name):
    primary_column_Name = 'Name'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(Table_Registers)
    response = table.delete_item(
        Key={
            primary_column_Name: D_Name
        }
    )


def notify_user_registered():
    Index_Register = get_RegisterName()
    for i in Index_Register:
        #print(i)
        Name = i[0]
        Email = i[1]
        Scan_reponse = Scan_Users(Name, Table_Users)
        if len(Scan_reponse) == 0:
            print(Name +" votre passeport n'est pas sorti")
        else:
            amazone_ses_mail(Name, Email, Scan_reponse[0]["URLImage"])
            Delete_Backup(Name)


if __name__ == "__main__":
    notify_user_registered()
