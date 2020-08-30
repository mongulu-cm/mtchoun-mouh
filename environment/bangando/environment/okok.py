
import random
import urllib.request
def dowload_image(url):
    name=random.randrange(1,1000)
    real_image=str(name)+".jpg"
    urllib.request.urlretrieve( url, real_image)
    
dowload_image("https://www.consulacam-marseille.fr/images/communiqueA-030215.jpg")