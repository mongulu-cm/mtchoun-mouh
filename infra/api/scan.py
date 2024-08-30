import sys
import shutil
sys.path.insert(0, "./package")
import requests
import urllib.request
import boto3
from bs4 import BeautifulSoup as soup
from boto3.dynamodb.conditions import Attr
import os
from config import passport_page
from notify import amazone_ses_mail

bucket_name = os.environ["BUCKET_NAME"]
Table_Links = os.environ["LINKS_TABLE"]
maintainer_mail = os.environ["MAINTAINER_MAIL"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
}


def S3_bucket_pictures(Picture_image, bucket_name):
    """
    This function takes a picture, uploads it to an S3 bucket, and then deletes the picture from the local directory

    :param Picture_image: The path to the image you want to upload to S3
    :param bucket_name: The name of the bucket you want to upload to
    """
    s3 = boto3.resource("s3")
    key_name = Picture_image.split("/tmp/")[1]
    s3.Object(bucket_name, key_name).put(Body=open(Picture_image, "rb"))
    os.remove(Picture_image)


def dowload_image(url):
    """
    It takes the url of the image as a parameter and downloads the image to the /tmp folder in the lambda environment

    :param url: The URL of the image to be downloaded
    :return: the real_image
    """
    name = url.split("/")[-1]
    real_image = f"/tmp/{str(name)}"  # image in jpg version ( only /tmp is writable in aws lambda)
    r = requests.get(url,stream=True,headers=headers)
    r.raw.decode_content = True
    r.raise_for_status()

    with open( real_image, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return real_image


def get_source_code(link):
    """
    It takes a link as an argument and returns the source code of the page

    :param link: the link of the web page you want to scrape
    :return: the source code of the web page
    """
    r = requests.get(link,headers=headers)
    r.raise_for_status()
    return soup(r.text,features="html.parser")


def filter(code_source_html):
    """
    > If there are images in the code source, return them, otherwise exit the program

    :param code_source_html: the html code of the page
    :return: A list of all the images in the html code
    """
    if imgs := code_source_html.findAll("img"):
        return imgs
    else:
        sys.exit("no image")


def insert_link(link_image):
    """
    It takes a link as an argument and inserts it into the DynamoDB table

    :param link_image: The link to the image that you want to store in the database
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Links)
    table.put_item(Item={"link": link_image})


def Scan_Link(link_image):
    """
    It scans the table for the link and returns the items

    :param link_image: The link of the image you want to scan for
    :return: A list of dictionaries.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Links)
    response = table.scan(FilterExpression=Attr("link").eq(link_image))
    return response["Items"]


def scan_consulate_passport_page():
    """
    It scans the consulate's passport page, filters the html code to get the links of the images, checks if the link is new,
    if it is, it downloads the image and uploads it to the S3 bucket
    """
    code_source_html = get_source_code(passport_page)
    tags = filter(code_source_html)
    srcs = [
        x.get("src") for x in tags if "communique" in x.get("src")
    ]  ## we select link with word communiqué
    notify_maintainer = False

    for src in srcs:
        link_image_initial = src.split("..")[1]
        real_link = f"https://www.consulacam-marseille.fr{link_image_initial}"
        Scan_reponse_link = Scan_Link(real_link)
        if len(Scan_reponse_link) == 0:
            print(f" new link: {real_link}")
            if not notify_maintainer:
                amazone_ses_mail("", maintainer_mail, real_link, maintainer=True)
                notify_maintainer = True

            insert_link(real_link)
            S3_bucket_pictures(dowload_image(real_link), bucket_name)
        else:
            print("This link is not a new one")


if __name__ == "__main__":
    scan_consulate_passport_page()
