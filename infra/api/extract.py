import boto3
from boto3 import client
from config import stopWords, images_url_path
import os
import zulip
from textractor import Textractor
from PIL import UnidentifiedImageError

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
    extractor = Textractor(region_name=region)
    errors_tab = []
    filtered_lines = []

    try:
        # Try to detect document text, catch UnidentifiedImageError if occurs
        document = extractor.detect_document_text(file_source=f"s3://{s3BucketName}/{ImageName}")
    except UnidentifiedImageError as e:
        print(f"UnidentifiedImageError: {str(e)} - Image: {ImageName}")
        errors_tab.append({"error": str(e), "image": ImageName})
        return errors_tab

    for line in document.lines:
        # Vérifie si aucun mot de stop_words n'est présent dans la ligne
        if not any(stop_word in str(line) for stop_word in stopWords):
            filtered_lines.append(str(line))
    
    for line in filtered_lines:
        try:
            UserName = line.split(". ")[1:] if "." in line else line
            if isinstance(UserName, list):
                UserName = ". ".join(UserName)
            if UserName != "":
                # We choose to save all names in lower case to avoid issues with stop words like 'DU'
                print(f"Username={UserName.lower()}")
                insert_dynamodb(UserName.lower(), ImageName)
        except Exception as e:
            print(e)
            errors_tab.append({str(e) + " " + str(line): ImageName})
            print(errors_tab)

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

        Delete_Image(bucket_name, image)
    Empty_Bucket(bucket_name)


if __name__ == "__main__":
    extract_names_from_images()
