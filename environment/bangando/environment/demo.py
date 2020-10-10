

from notify import Scan_Users

Table_Users="Demo_Users"

if __name__ == "__main__":
    Name = "METANGMO TSOBZE BILL"
    Scan_reponse=Scan_Users(Name.lower(),Table_Users)
    print(Scan_reponse[0]["URLImage"])

