

import boto3

s3BucketName="djansang"
ImageName="136.jpg"
MY_Name="METANGMO"
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
    if MY_Name in line[1]:
        print ("votre passeport est sorti, des bisous")
        

