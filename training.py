# https://github.com/dpwe/audfprint
from audfprint import audfprint
import os

DB_FILE = "db.pklz"


# Create the training data
def train():
    print("Training model")

    if os.path.isfile(DB_FILE):
        os.remove(DB_FILE)

    snippets = ""
    for file in os.listdir("transitions"):
        if ".mp3" in file:
            snippets += "transitions/" + file + " "
    audfprint.main(("audfprint new --dbase db.pklz --maxtime 524288 --density 20 --shifts 4 " + snippets.strip()).split(" "))


if __name__ == "__main__":
    train()
