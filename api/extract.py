import boto3
from boto3 import client
from config import stopWords, images_url_path
import os


def Images_in_Bucket(Bucket_Name):
    """
    This function takes in a bucket name and returns a list of all the images in that bucket

    :param Bucket_Name: The name of the bucket you want to list the images from
    :return: A list of all the images in the bucket.
    """
    s3 = client("s3")
    Image_List = []
    if "Contents" in s3.list_objects(Bucket=Bucket_Name):
        Image_List.extend(
            key["Key"] for key in s3.list_objects(Bucket=Bucket_Name)["Contents"]
        )

    return Image_List


def Empty_Bucket(Bucket_Name):
    """
    It takes a bucket name as an argument, and then deletes all the objects in that bucket.

    :param Bucket_Name: The name of the bucket you want to empty
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(Bucket_Name)
    bucket.objects.all().delete()


def Delete_Image(Bucket_Name, ImageName):
    """
    This function deletes an image from an S3 bucket

    :param Bucket_Name: The name of the bucket you want to upload the image to
    :param ImageName: The name of the image you want to delete
    """
    s3 = client("s3")
    s3.delete_object(Bucket=Bucket_Name, Key=ImageName)


def insert_dynamodb(User, ImageName):
    """
    > It takes the user name and the image name as input, and then it inserts a new item into the DynamoDB table

    :param User: The user name of the person who uploaded the image
    :param ImageName: The name of the image that was uploaded to S3
    """
    region = os.environ["REGION"]
    Table_Users = os.environ["USERS_TABLE"]
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(Table_Users)
    table.put_item(
        Item={"UserName": User, "URLImage": f"{images_url_path}/{ImageName}"}
    )


def Extract_Users(s3BucketName, ImageName):  # sourcery no-metrics
    """
    It takes an image name and an S3 bucket name as input, and then uses Amazon Textract to extract the names of the people
    in the image

    :param s3BucketName: The name of the S3 bucket that contains the image
    :param ImageName: The name of the image file that you want to extract text from
    """
    region = os.environ["REGION"]
    textract = boto3.client("textract", region_name=region)
    reponse = textract.detect_document_text(
        Document={"S3Object": {"Bucket": s3BucketName, "Name": ImageName}}
    )
    # print(reponse)
    columns = []
    lines = []
    for item in reponse["Blocks"]:
        if item["BlockType"] == "LINE":
            column_found = False
            for index, column in enumerate(columns):
                bbox_left = item["Geometry"]["BoundingBox"]["Left"]
                bbox_right = (
                    item["Geometry"]["BoundingBox"]["Left"]
                    + item["Geometry"]["BoundingBox"]["Width"]
                )
                bbox_centre = (
                    item["Geometry"]["BoundingBox"]["Left"]
                    + item["Geometry"]["BoundingBox"]["Width"] / 2
                )
                column_centre = column["left"] + column["right"] / 2

                if (bbox_centre > column["left"] and bbox_centre < column["right"]) or (
                    column_centre > bbox_left and column_centre < bbox_right
                ):
                    # Bbox appears inside the column
                    lines.append([index, item["Text"]])
                    column_found = True
                    break
            if not column_found:
                columns.append(
                    {
                        "left": item["Geometry"]["BoundingBox"]["Left"],
                        "right": item["Geometry"]["BoundingBox"]["Left"]
                        + item["Geometry"]["BoundingBox"]["Width"],
                    }
                )
                lines.append([len(columns) - 1, item["Text"]])

    lines.sort(key=lambda x: x[0])

    filtered_lines = []
    for line in lines:
        # print(line[1])
        detected_stop_words = [x for x in stopWords if x in line[1]]
        if not detected_stop_words:
            filtered_lines.append(line)
    # TODO: Create a custom iterator: https://www.programiz.com/python-programming/iterator
    iter_lines = iter(filtered_lines)
    while True:
        errors_tab = []
        try:
            # get the next item
            line = next(iter_lines)
            # print(line[1])
            raise IndexError

            UserName = ""
            if " " not in line[1]:

                # print ( "prev line:"+line[1])
                line = next(iter_lines)
                # Sometimes the number. and names are detected separetely and not in order
                # In this case, the next line can not be the name but also number. so we iterate until there is a name
                while " " not in line[1]:
                    line = next(iter_lines)

                # print ( "next line:"+line[1])
                UserName = line[1]

            else:
                UserName = line[1].split(". ")[1] if "." in line[1] else line[1]
            # print(line)
            if UserName != "":
                # We choosed to save all the names in lower former instead of upper because of the DU stopWord
                # Indeed if upper names , all persons DU like DURAND in their names will not be detected.
                insert_dynamodb(UserName.lower(), ImageName)
                print(f"Username={UserName}")

        except StopIteration:
            break

        except IndexError as e:
            print(e)
            errors_tab.append(e)
            print(f"related image:{ImageName}")

    print(errors_tab)
    # TODO : stocker les erreurs dans un tableau
    # TODO : print le tableau et return


def extract_names_from_images():
    """
    > It takes all the images in the bucket, extracts the names of the people in the images, and then deletes the images
    from the bucket
    """
    bucket_name = os.environ["BUCKET_NAME"]
    Image_List = Images_in_Bucket(bucket_name)
    for image in Image_List:
        print(f"-------> Image name: {image}")
        # TODO : recuperer le tableau d'erreurs et envoyer le mail
        Extract_Users(bucket_name, image)
        Delete_Image(
            bucket_name, image
        )  # so that if it executed 2 times extracted images will not be there
    Empty_Bucket(bucket_name)


if __name__ == "__main__":
    extract_names_from_images()
