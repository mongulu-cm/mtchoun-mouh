import boto3
from boto3 import client
from config import stopWords, images_url_path
import os


def Images_in_Bucket(Bucket_Name):
    s3 = client('s3')
    Image_List = []
    if "Contents" in s3.list_objects(Bucket=Bucket_Name):
        for key in s3.list_objects(Bucket=Bucket_Name)['Contents']:
            Image_List.append(key['Key'])

    return Image_List


def Empty_Bucket(Bucket_Name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(Bucket_Name)
    bucket.objects.all().delete()


def Delete_Image(Bucket_Name, ImageName):
    s3 = client('s3')
    s3.delete_object(Bucket=Bucket_Name, Key=ImageName)


def insert_dynamodb(User, ImageName):
    region = os.environ['REGION']
    Table_Users = os.environ['USERS_TABLE']
    dynamodb = boto3.resource('dynamodb',region_name=region)
    table = dynamodb.Table(Table_Users)
    table.put_item(
        Item={
            'UserName': User,
            'URLImage': images_url_path + "/" + ImageName
        }
    )


def Extract_Users(s3BucketName, ImageName):
    region = os.environ['REGION']
    textract = boto3.client('textract', region_name=region)
    reponse = textract.detect_document_text(
        Document={
            'S3Object':
                {
                    'Bucket': s3BucketName,
                    'Name': ImageName
                }

        }
    )
    # print(reponse)
    columns = []
    lines = []
    for item in reponse["Blocks"]:
        if item["BlockType"] == "LINE":
            column_found = False
            for index, column in enumerate(columns):
                bbox_left = item["Geometry"]["BoundingBox"]["Left"]
                bbox_right = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"]
                bbox_centre = item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"]["Width"] / 2
                column_centre = column['left'] + column['right'] / 2

                if (bbox_centre > column['left'] and bbox_centre < column['right']) or (
                        column_centre > bbox_left and column_centre < bbox_right):
                    # Bbox appears inside the column
                    lines.append([index, item["Text"]])
                    column_found = True
                    break
            if not column_found:
                columns.append({'left': item["Geometry"]["BoundingBox"]["Left"],
                                'right': item["Geometry"]["BoundingBox"]["Left"] + item["Geometry"]["BoundingBox"][
                                    "Width"]})
                lines.append([len(columns) - 1, item["Text"]])

    lines.sort(key=lambda x: x[0])

    filtered_lines = []
    for line in lines:
        # print(line[1])
        detected_stop_words = [x for x in stopWords if x in line[1]]
        if len(detected_stop_words) == 0:
            filtered_lines.append(line)
        else:
            pass
            # print("line filtered")

    # TODO: Create a custom iterator: https://www.programiz.com/python-programming/iterator
    iter_lines = iter(filtered_lines)
    while True:
        try:
            # get the next item
            line = next(iter_lines)
            # print(line[1])

            UserName = ""
            if not " " in line[1]:

                # print ( "prev line:"+line[1])
                line = next(iter_lines)
                # Sometimes the number. and names are detected separetely and not in order
                # In this case, the next line can not be the name but also number. so we iterate until there is a name
                while not " " in line[1]:
                    line = next(iter_lines)

                # print ( "next line:"+line[1])
                UserName = line[1]

            else:
                if "." in line[1]:
                    UserName = line[1].split(". ")[1]
                else:
                    # Sometimes the number. and names are detected separetely and not in order
                    # In this case, line[1] is directly the username
                    UserName = line[1]

            # print(line)
            if UserName != "":
                # We choosed to save all the names in lower former instead of upper because of the DU stopWord
                # Indeed if upper names , all persons DU like DURAND in their names will not be detected.
                insert_dynamodb(UserName.lower(), ImageName)
                print("Username=" + UserName)

        except StopIteration:
            break

        except IndexError as e:
            print(e)
            print("related image:" + ImageName)


def extract_names_from_images():
    bucket_name = os.environ['BUCKET_NAME']
    Image_List = Images_in_Bucket(bucket_name)
    for image in Image_List:
        print("-------> Image name: " + image)
        Extract_Users(bucket_name, image)
        Delete_Image(bucket_name, image)  # so that if it executed 2 times extracted images will not be there
    Empty_Bucket(bucket_name)


if __name__ == "__main__":
    extract_names_from_images()
