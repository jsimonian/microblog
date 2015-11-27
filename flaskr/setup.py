import flaskr
from config import ADMIN_PASSWORD
pwd = input("Warning: You are about to delete your current Flaskr System.\n\
Please input the Admin Password to proceed.\n")
if pwd == ADMIN_PASSWORD:
    flaskr.init_db()
    print("Flaskr is set up!")
else:
    print("Incorrect password, closing setup.")
