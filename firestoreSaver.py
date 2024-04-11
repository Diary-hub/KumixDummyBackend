import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import glob
import json

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


path = "Comics/"
extension = "json"
os.chdir(path)
result = glob.glob("*.{}".format(extension))

comicID = []

for comic in result:
    comicID.append(comic.split(".")[0])


with open("29.json", encoding="utf-8") as comic:
    data = json.load(comic)
    print(data)
    doc_ref = db.collection("Comics").document("30")
    doc_ref.set(data)


for id in comicID:
    # doc_ref = db.collection("Comics").document(id)
    # doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})

    None
