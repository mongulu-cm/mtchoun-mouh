import sys

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


def S3_bucket_pictures(Picture_image, bucket_name):
    s3 = boto3.resource("s3")
    key_name = Picture_image.split("/tmp/")[1]
    s3.Object(bucket_name, key_name).put(Body=open(Picture_image, "rb"))
    os.remove(Picture_image)


def dowload_image(url):
    ###  this function allows you to download the images  by providing the parameter url
    name = url.split("/")[-1]
    real_image = f"/tmp/{str(name)}"  # image in jpg version ( only /tmp is writable in aws lambda)
    urllib.request.urlretrieve(url, real_image)
    return real_image


def get_source_code(link):
    ##this function allows to scrape on  a web page   by providing his link
    r = requests.get(link)
    if r.status_code == 200:
        return soup(r.text)
    else:
        sys.exit("invalid")


def filter(code_source_html):
    ## this function allows you to retrieve all the links of the images
    imgs = code_source_html.findAll("img")
    if imgs:
        return imgs
    else:
        sys.exit("no image")


def insert_link(link_image):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Links)
    table.put_item(Item={"link": link_image})


def Scan_Link(link_image):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(Table_Links)
    response = table.scan(FilterExpression=Attr("link").eq(link_image))
    return response["Items"]


def scan_consulate_passport_page():
    code_source_html = get_source_code(passport_page)
    tags = filter(code_source_html)
    srcs = [
        x.get("src") for x in tags if "communique" in x.get("src")
    ]  ## we select link with word communiqué
    notify_maintainer = False

    for src in srcs:
        src.split("..")
        link_image_initial = src.split("..")[1]
        real_link = "https://www.consulacam-marseille.fr" + link_image_initial
        Scan_reponse_link = Scan_Link(real_link)
        if len(Scan_reponse_link) == 0:
            print(" new link: " + real_link)
            if not notify_maintainer:
                amazone_ses_mail("", maintainer_mail, real_link, maintainer=True)
                notify_maintainer = True

            insert_link(real_link)
            S3_bucket_pictures(dowload_image(real_link), bucket_name)
        else:
            print("This link is not a new one")


if __name__ == "__main__":
    scan_consulate_passport_page()
