import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from registre import get_RegisterName
from boto3.dynamodb.conditions import Attr
from boto3 import client


def Images_in_Bucket(Bucket_Name):
    s3 = client('s3') 
    Image_List=[]
    for key in s3.list_objects(Bucket=Bucket_Name)['Contents']:
        Image_List.append(key['Key'])
    for i in Image_List:
        Extract_Users(Bucket_Name,i)
    return Image_List
    


def Delete_Backup(D_Name):
    primary_column_Name='Name'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Register')
    response = table.delete_item(
        Key={
            primary_column_Name:D_Name
        }
    )

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


def Scan_Users(UserName):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.scan(
        FilterExpression=Attr('UserName').eq(UserName)
    )
    return response['Items']
    
   
    


def Extract_Users(s3BucketName,ImageName):
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
    
    lines.sort(key=lambda x: x[0])
    
    
    # TODO: Create a custom iterator: https://www.programiz.com/python-programming/iterator
    iter_lines = iter(lines)
    while True:
        try:
            # get the next item
            line = next(iter_lines)
            Username = ""
            if not " " in line[1]:
                line = next(iter_lines)
                UserName = line[1]
                
            else:
                if "."  in line[1] :
                    UserName = line[1].split(". ")[1]
            
            if UserName != "":
                insert_dynamodb(UserName)
                #print(UserName)
                
        except StopIteration:
            break
            

Images_in_Bucket("djansang")

    
Index_Register=get_RegisterName()
for i in Index_Register:
    print(i)
    Name=i[0]
    Email=i[1]
    Scan_reponse=Scan_Users(Name)  
    if len(Scan_reponse)==0:
       print(" votre passeport n'est pas sorti")
    else:
        amazone_ses_mail(Email)
        Delete_Backup(Name)

