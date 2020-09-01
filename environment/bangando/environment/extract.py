
import boto3
from boto3.dynamodb.conditions import Key

s3BucketName="djansang2"
ImageName="244.jpg"
MY_Name="NGO LOGSEN Charlotte"


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
    
    lines.sort(key=lambda x: x[0])
    for line in lines:
        #print(line[1])
        if "."  in line[1] :
            UserName = line[1].split(". ")[1]
            #print(UserName)
            insert_dynamodb(UserName)
        
            
            
Query_reponse=Query_Users(MY_Name)  
if len(Query_reponse)==0:
    print(" votre passeport n'est pas sorti")
else:
    print("votre passeport est sorti")
main()
