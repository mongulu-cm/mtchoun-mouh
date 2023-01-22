import os 
from registre import insert_dynamodb_registered, verifying_Register_mail
from scan import scan_consulate_passport_page
from extract import extract_names_from_images
from notify import notify_user_registered, Scan_Users, amazone_ses_mail_registration
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk import capture_exception
import boto3

# Configure Sentry SDK
sentry_dns=os.environ["SENTRY_DNS"]

sentry_sdk.init(
    dsn= sentry_dns,
    integrations=[AwsLambdaIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


def register_handler(event, context):

    import json
    
    try:

        # This is because of Lambda Proxy Integration: https://frama.link/rezj9B9C
        body = json.loads(event["body"])
        name = body["name"]
    
        if "email" in body:
            
            email = body["email"]
            insert_dynamodb_registered(name, email)
            amazone_ses_mail_registration(name, email)
    
            # headers for CORS in proxy mode: https://frama.link/vY7ESUz4
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "GET,OPTIONS,POST,PUT",
                },
                "body": json.dumps(
                    {
                        "message": f" Hello {name}, your email address is {email}",
                    }
                ),
            }
    
        else:
            # demo case
            Scan_reponse = Scan_Users(name.lower(), "Demo_Users")
            image_url = Scan_reponse[0]["URLImage"]
            # print(image_url)
    
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "GET,OPTIONS,POST,PUT",
                },
                "body": json.dumps(
                    {
                        "message": f" {image_url}",
                    }
                ),
            }
    except Exception as e:
         capture_exception(e)
         

def scan_handler(event, context):    
    try:

        print(event)
        scan_consulate_passport_page()
        extract_names_from_images()
        notify_user_registered()

    except Exception as e:
         capture_exception(e)
