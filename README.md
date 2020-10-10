         ___        ______     ____ _                 _  ___  
        / \ \      / / ___|   / ___| | ___  _   _  __| |/ _ \ 
       / _ \ \ /\ / /\___ \  | |   | |/ _ \| | | |/ _` | (_) |
      / ___ \ V  V /  ___) | | |___| | (_) | |_| | (_| |\__, |
     /_/   \_\_/\_/  |____/   \____|_|\___/ \__,_|\__,_|  /_/ 
 ----------------------------------------------------------------- 


Hi there! Welcome to AWS Cloud9!

To get started, create some files, play with the terminal,
or visit https://docs.aws.amazon.com/console/cloud9/ for our documentation.

Happy coding!


Constraints ( 15 juillet 2020 )
 - vye au lieu de vve
 - Benoft au lieu de Benoit ( problème i accent circonflexe)
 - epse au lieu de epouse et sans accent
 - Ralssa au lieu de Raissa ( problème tréma)
 - Joel/Gaetan/Raphael au lieu de X avec tréma
 - Ceux qui ont un seul nom pas détecté comme KAMTE/TCHIENO juste
 - KWAY!/ETOUND! au lieu de KWAYI/ETOUDI prénom finissant par I
 - Irene au lieu d Irène ( pas d'accent globalement)
 - II comme kossa 4 disons - pas supoorté chiffres romains


Travail A faire:
 - Le bucket pour les images scannées ainsi que DynamoDB dans la zone frankfort
 - Créer des variables d'environnement lambda pour config.py dans l'objectif d'avoir une table de démo
 - Créer un fichier config.py dans lequel seront mis:
        * le nom du bucket des images
        * le nom des différentes tables dynamodb
 - Changer le sujet et le body du mail disant que le passeport est sorti
 - Mettre aussi dans config.py les stopWords
 - Faire l'intégration avec la page web .
 

 - Faire un fichier demo.py de demo qui query le communiqué du 22/09/2020
      Travail à main
        * Récupérer toutes les images du consulat 
        * Ne garder que les communiqués du 22/09/2020
        * Créer des tables Demo_X ou X est le nom de la table
        * Remplacer le nom des tables en question dans config.py
      Travail de code:
        * Modifier le code de scan pour stocker à la fois le nom et l'url de l'images
        * Exécuter ce code
        * Créer un fichier query.py qui prend en paramètre le nom de l'utilisateur et si celui-ci existe retourne l' URL.
