
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import subprocess


s3BucketName="djansang2"
ImageName="244.jpg"




MY_Name="NGO LOGSEN Charlotte"
MY_User_mail= "tagnetchanafabiolacorinne@gmail.com "

     

def verifying_recipient_mail(RECIPIENT):
    subprocess.run(["aws","ses","verify-email-identity","--email-address", RECIPIENT])
    
    
    
    
def amazone_ses_mail(RECIPIENT):
    SENDER = "Sender Name <tagnefabiola97@gmail.com>"
    AWS_REGION = "us-east-1"
    SUBJECT = "consulat_du_CAMEROUN"
    BODY_TEXT = ("Votre passeporte est sortie  (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )
    BODY_HTML = """<html>
          <head></head>
                <body>
                  <h1>Amazon SES Test (SDK for Python)</h1>
                  <p>This email was sent with
                    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
                    <a href='https://aws.amazon.com/sdk-for-python/'>
                      AWS SDK for Python (Boto)</a>.</p>
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



def  insert_dynamodb(User):
    dynamodb = boto3.resource('dynamodb')
    table =dynamodb.Table('Users')
    table.put_item(
        Item={
            'UserName':User
        }
    )

def Query_Users(UserName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.query(
        KeyConditionExpression=Key('UserName').eq(UserName)
    )
    return response['Items']


def main():
    textract = boto3.client('textract')
    reponse=textract.detect_document_text(
        Document ={
            'S3Object':
                {
                'Bucket':s3BucketName,
                'Name':ImageName
                }
            
        }
        )
    #print(reponse)
    columns = []
    lines = []
    for item in reponse["Blocks"]:
          if item["BlockType"] == "LINE":
            column_found=False
            for index, column in enumerate(columns):
                bbox_left = item["Geometry"]["BoundingBox"]["Left"]
                bbox_right = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]
                bbox_centre = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]/2
                column_centre = column['left'] + column['right']/2
    
                if (bbox_centre > column['left'] and bbox_centre < column['right']) or (column_centre > bbox_left and column_centre < bbox_right):
                    #Bbox appears inside the column
                    lines.append([index, item["Text"]])
                    column_found=True
                    break
            if not column_found:
                columns.append({'left':item["Geometry"]["BoundingBox"]["Left"], 'right':item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]})
                lines.append([len(columns)-1, item["Text"]])
          elif item["BlockType"] == "TABLE":
              print("table")
    
    lines.sort(key=lambda x: x[0])
    for line in lines:
        #print(line[1])
        if "."  in line[1] :
            UserName = line[1].split(". ")[1]
            print(UserName)
            insert_dynamodb(UserName)
        
            
 


 
Query_reponse=Query_Users(MY_Name)  
if len(Query_reponse)==0:
   print(" votre passeport n'est pas sorti")
else:
    verifying_recipient_mail(MY_User_mail)
    amazone_ses_mail(MY_User_mail)
main()
