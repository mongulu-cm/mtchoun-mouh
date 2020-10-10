

from notify import Scan_Users
from sys import argv

Table_Users="Demo_Users"

if __name__ == "__main__":
    Name = argv[1]
    Scan_reponse=Scan_Users(Name.lower(),Table_Users)
    print(Scan_reponse[0]["URLImage"])

