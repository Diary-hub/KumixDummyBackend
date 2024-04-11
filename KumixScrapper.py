import json
import requests
from flask import Flask, jsonify, request
import simplejson

app = Flask(__name__)

baseUrl = "https://kurdcomic.net/"
baseGetUrl = "https://kurdcomic.net/api/client/get/"

likedNumbers = baseGetUrl + "likeNumber/"
viewComicPage = baseGetUrl + "view_comic/"

comicCover = baseUrl + "image_comic/"
issuePage = baseUrl = "image_band/"

allComics = baseGetUrl + "comics"

searchByName = baseGetUrl + "search/"


allComicsIDs = [
    74,
    29,
    76,
    75,
    78,
    39,
    79,
    73,
    46,
    68,
    49,
    58,
    44,
    77,
    43,
    47,
    71,
    62,
    63,
    41,
    72,
    69,
    40,
    60,
    67,
    55,
    57,
    54,
    59,
    70,
    45,
    42,
    65,
    48,
    50,
    53,
    61,
    64,
    66,
    51,
    52,
    56,
]


def get_data(api, body=None):
    if body is not None:
        response = requests.post(f"{api}", json=body)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Hello person, there's a {response.status_code} error with your request"
    else:
        response = requests.get(f"{api}")
        if response.status_code == 200:
            return response.json()
        else:
            return f"Hello person, there's a {response.status_code} error with your request"


# /issues?id=74&number=1
@app.route("/issuesPage", methods=["GET"])
def getIssues():
    comicID = request.args.get("id")

    issueNumber = request.args.get("number")
    api = baseGetUrl + f"read_comic/{comicID}?band_number={issueNumber}"
    result = get_data(api=api)
    print("THIS IS IT")
    datas = result["data"]
    return datas


# /comics?page={1,2,3}
@app.route("/comics", methods=["get"])
def getComics():
    page = request.args.get("page")
    body = {
        "page": page,
        "selected_type": -1,
        "selected_genre": -1,
        "most_view": "false",
        "order_by": "true",
        "date": "",
    }
    api = allComics
    result = get_data(api=api, body=body)
    datas = result["data"]["data"]

    allComicsID = []
    for id in datas:
        allComicsID.append(id["id"])

    if len(datas) > 0:
        return json.dumps(allComicsID)
    else:
        return "There is No Page With That Page Number Stupid"


# /search?name=spider
@app.route("/search", methods=["GET"])
def searchComic():
    comicName = request.args.get("name")
    api = searchByName + comicName
    result = get_data(api=api)
    datas = result["data"]["data"]
    if len(datas) > 0:
        return datas
    else:
        return "Sorry We Have No Comic Contains That Name!"


# Get Issues By Number
def getIssuesByNumber(comicID, issueNumber):
    api = baseGetUrl + f"read_comic/{comicID}?band_number={issueNumber}"
    result = get_data(api=api)
    datas = result["data"]
    return datas


# /issues?id=74
@app.route("/issues", methods=["GET"])
def getComicDetails():
    comicID = request.args.get("id")
    api = viewComicPage + comicID
    result = get_data(api=api)
    data = result["data"]
    geners = data["genres"]
    generesList = []
    for genre in geners:
        # print("" + genre["genres"]["name"])
        generesList.append(genre["genres"]["name"])

    Issues = []

    for i in range(0, result["comic_band_number"]):
        Issues.append(getIssuesByNumber(data["id"], i + 1))

    details = {
        "ComicID": data["id"],
        "Name": data["name"],
        "Description": data["kurta"],
        "NumberOfIssues": result["comic_band_number"],
        "CoverImage": data["cover"],
        "WatchAge": data["gwnjawy_taman"],
        "IsEnded": data["is_end"],
        "PublishDate": data["publish_date"],
        "Rating": data["rating"],
        "Views": data["views"],
        "Genres": generesList,
        "Issues": Issues,
    }
    with open("Comics/" + str(data["id"]) + ".json", "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=4)
    return details


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
