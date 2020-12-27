from diagrams import Diagram, Cluster
from diagrams.aws.network import Route53
from diagrams.aws.storage import S3
from diagrams.aws.mobile import APIGateway
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import  Eventbridge
from diagrams.programming.language import  Python, Javascript
from diagrams.aws.database import DDB
from diagrams.aws.engagement import SES
from diagrams.aws.ml import Textract

with Diagram("mtchou_mouh_Architecture", show=False):

    with Cluster(" Envoie_de_la notification "):
        flux_2 = Eventbridge("planifie l'execution \nde la fonction\nscan_user du lundi \nau vendredi à 8H00") >>Lambda("Handler:lambdascan_handeler")

    #with Cluster("Enregistrement_de_l'utilisateur "):
        flux_1 = Route53("redirige le trafic \n de mtchou-mouh.mongulu.cm \n vers le bucket S3 de meme nom") >> S3(
            "3 PAGES WEB :\n-index.html\n-demo.html\n-error.html") >> APIGateway(
            "-OPTIONS:résout\nproblèmeCORS\n-POST:donne les\n informations à LAMBDA") >> Lambda(
            "Handler:lambda.register_handler\n-Enregistrement information dans\n DynamoDB table Register\n-Envoie mail de verification \nvia AmazoneSES")

    with Cluster("Programming"):
        languages=[Python("BackEnd"),
                   Javascript("FrontEnd")]

    with Cluster("BackEnd_1"):
        Backend_1=[DDB("DataBase"),
                   SES("verification")]
    with Cluster("BackEnd_2"):
        Backend_2=[S3("storage"),
                   SES("notifier"),
                   DDB("DataBase"),
                   Textract("Extraction")]

    languages >> flux_1 >> Backend_1
    languages >> flux_2 >> Backend_2