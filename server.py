import aiohttp
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import asyncio

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

auth = aiohttp.BasicAuth()


uri = ""

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))




async def getFirstParams():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'https://metron.cloud/api/series/?cv_id=&missing_cv_id=&modified_gt=&name=&publisher_id=&publisher_name=&series_type=&series_type_id=&volume=&year_began=2022&year_end=2023',
                headers=headers, auth=auth) as response:
            json_output = await response.json()
            return json_output


async def getSecondParams(id):
    link = f"https://metron.cloud/api/series/{id}/issue_list/"
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers, auth=auth) as response:
            json_output = await response.json()
            return json_output


async def AddDataRecord(collection,cID,cYearBegan,cIssueCount,ctitle,cImage):
    new_document = {
        "cID": cID,
        "ctitle": ctitle,
        "cYearBegan": cYearBegan,
        "cIssueCount": cIssueCount,
        "cImage": cImage
        # Add other fields as needed
    }
    result = collection.insert_one(new_document)
    return result


async def main():
    try:
        # Select the database and collection
        db = client.comics
        collection = db.data

        dd = await getFirstParams()
        print(dd)

        for i in dd['results']:
            cID = i['id']
            cYearBegan = i['year_began']
            cIssueCount = i['issue_count']

            json_outputOne = await getSecondParams(cID)

            ctitle = json_outputOne['results'][0]['series']['name']
            cImage = json_outputOne['results'][0]['image']

            await AddDataRecord(collection,cID,cYearBegan,cIssueCount,ctitle,cImage)

        # Retrieve all documents in the collection
        result = collection.find()

        # Print the documents
        for document in result:
            print(document)

        # Close the connection
        client.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())


# from flask import Flask, render_template, request, jsonify
# import json
# from flask_cors import CORS
# import sys
# import mokkari


# app = Flask(__name__)
# CORS(app)

# m = mokkari.api('DocXy', 'Dihack@2002')
# # this_week = m.series_list({ "publisher_name": "marvel", "limit" : 2})
# # this_week = m.series(1530)
# this_week = m.issues_list({'id': 1530})

# obj = this_week.__dict__

# print(obj)

# list = []

# for i in this_week:
#     print("The First Print: ",i.__dict__)
#     list.append(i.__dict__)
#     break
