import boto3
from boto3 import client
from config import stopWords, images_url_path
import os
import zulip


def Images_in_Bucket(Bucket_Name):
    """Gets a list of all image names in an S3 bucket.

    Args:
        Bucket_Name (str): The name of the S3 bucket

    Returns:
        list: A list containing all the image names in the given S3 bucket
    """
    s3 = client("s3")
    Image_List = []
    if "Contents" in s3.list_objects(Bucket=Bucket_Name):
        Image_List.extend(
            key["Key"] for key in s3.list_objects(Bucket=Bucket_Name)["Contents"]
        )

    return Image_List


def Empty_Bucket(Bucket_Name):
    """Deletes all objects in an S3 bucket.

    This function takes the name of an S3 bucket, connects to the S3 service
    using boto3, gets a bucket resource object for the specified bucket,
    and calls delete() on all objects in the bucket to empty it.

    Args:
        Bucket_Name (str): The name of the S3 bucket to empty

    Returns:
        None

    Raises:
        Any exceptions raised by boto3 calls

    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(Bucket_Name)
    bucket.objects.all().delete()


def Delete_Image(Bucket_Name, ImageName):
    """Deletes an image from an S3 bucket.

    Args:
        Bucket_Name (str): The name of the S3 bucket.
        ImageName (str): The key name of the image file to delete.

    Returns:
        None

    Raises:
        Any exceptions raised by boto3 delete_object call.

    """
    s3 = client("s3")
    s3.delete_object(Bucket=Bucket_Name, Key=ImageName)


def insert_dynamodb(User, ImageName):
    """Inserts a new item into a DynamoDB table.

    Args:
        User (str): The user name of the person who uploaded the image.
        ImageName (str): The name of the image that was uploaded to S3.

    Returns:
        None

    Raises:
        Any exceptions raised by boto3 put_item call.

    """
    region = os.environ["REGION"]
    Table_Users = os.environ["USERS_TABLE"]
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(Table_Users)
    table.put_item(
        Item={"UserName": User, "URLImage": f"{images_url_path}/{ImageName}"}
    )


def Extract_Users(s3BucketName, ImageName):  # sourcery no-metrics
    """Extracts user information from an image in an S3 bucket.

    Args:
        s3BucketName (str): The name of the S3 bucket containing the image.
        ImageName (str): The name of the image file in the S3 bucket.

    Returns:
        list: A list of extracted user information dicts.
    """
    region = os.environ["REGION"]
    textract = boto3.client("textract", region_name=region)
    reponse = textract.detect_document_text(
        Document={"S3Object": {"Bucket": s3BucketName, "Name": ImageName}}
    )
    # print(reponse)
    columns = []
    lines = []
    errors_tab = []
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

        except Exception as e:
            print(e)
            errors_tab.append({str(e) + " " + str(line): ImageName})
            print(errors_tab)
            # print(f"related image:{ImageName}")

    return errors_tab


def extract_names_from_images():
    """
    Extracts names from images using OCR.

    Returns:
        list: A list of names extracted from the images.
    """
    zulip_client = zulip.Client(
        email="errorbot-bot@mongulu.zulipchat.com",
        api_key=os.environ["API_KEY"],
        site="https://mongulu.zulipchat.com",
    )

    bucket_name = os.environ["BUCKET_NAME"]
    Image_List = Images_in_Bucket(bucket_name)
    # Image_List = ["communique-071218-A.jpg"]
    for image in Image_List:
        print(f"-------> Image name: {image}")
        # TODO : recuperer le tableau d'erreurs et envoyer le mail
        errors_tab = Extract_Users(bucket_name, image)
        for errors in errors_tab:

            request = {
                "type": "stream",
                "to": "mtchoun-mouh",
                "topic": "Errors",
                "content": errors,
            }

            result = zulip_client.send_message(request)
        print(errors_tab)

        Delete_Image(
            bucket_name, image
        )  # so that if it executed 2 times extracted images will not be there
    Empty_Bucket(bucket_name)


if __name__ == "__main__":
    extract_names_from_images()
