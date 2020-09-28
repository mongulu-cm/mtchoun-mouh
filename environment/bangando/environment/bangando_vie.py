
#!/usr/bin/python
import random
import urllib.request
import requests
import sys
import boto3
from bs4 import BeautifulSoup  as soup

def dowload_image(url):
###  this function allows you to download the images  by providing the parameter url 
    name=random.randrange(1,1000)
    real_image=str(name)+".jpg"    #image in jpg version 
    urllib.request.urlretrieve( url, real_image)
    
    

def get_source_code(link):
##this function allows to scrape on  a web page   by providing his link  
    r=requests.get(link)
    if r.status_code == 200:
        return soup(r.text)
    else:
        sys.exit("invalid")
            

def filter(code_source_html):
## this function allows you to retrieve all the links of the images 
    imgs=code_source_html.findAll("img")
    if imgs:
        return imgs
    else:
        sys.exit("no image")
        
def main():
    code_source_html=get_source_code("https://www.consulacam-marseille.fr/index.php?p=consulat-cameroun-passeports")
    tags=filter(code_source_html)
    srcs= [x.get("src") for x in tags if "communique" in x.get("src")] ## we select link with word communiqué 
    Link=[]
    for src in srcs :
        src.split("..")
        link_image_initial=src.split("..")[1]
        real_link="https://www.consulacam-marseille.fr"+link_image_initial
        if real_link not in Link:
            Link.append(real_link)
            dowload_image(real_link)
    print(Link)
    
main()
   
