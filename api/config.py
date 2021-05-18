import os

#List of words that is used to filter lines
stopWords = ["Phone","Cours Pierre","Tel.","www.consulacam-marseille.fr","REPUBLIQUE","Paix","Marseille","Cameroun",
             "passeports","presentation","REPUBLIC","Cameroon","Peace","CCM","COMMUNIQUE","DU","OF","N°","2020",
             "2021","2022","2023","2024","2025","s'agit","recepisse"]

#consulat
passport_page="https://www.consulacam-marseille.fr/index.php?p=consulat-cameroun-passeports"
images_url_path="https://www.consulacam-marseille.fr/images"

region=os.environ['REGION']

# Nom du bucket
bucket_name=os.environ['BUCKET_NAME']

# Tables
Table_Users=os.environ['USERS_TABLE']
Table_Links=os.environ['LINKS_TABLE']
Table_Registers=os.environ['REGISTERS_TABLE']

# Maintainer
maintainer_mail=os.environ['MAINTAINER_MAIL']
