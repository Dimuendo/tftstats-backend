import flask
from tftcomps import getData
from flask import request, jsonify
from summoner import Summoner
import pymongo
from dotenv import load_dotenv
import os

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "<h1>TFTStats.gg API</h1>"

@app.route('/compStats', methods=['GET'])
def displayCompStats():
    return jsonify(tftDataDict['compStats'])

@app.route('/itemPercentages', methods=['GET'])
def displayItemPercentages():
    return jsonify(tftDataDict['itemPercentages'])

@app.route('/unitPercentages', methods=['GET'])
def displayUnitPercentages():
    return jsonify(tftDataDict['unitPercentages'])

@app.route('/traitPercentages', methods=['GET'])
def displayTraitPercentages():
    return jsonify(tftDataDict['traitPercentages'])

@app.route('/commonItems', methods=['GET'])
def displayCommonItems():
    return jsonify(tftDataDict['commonItems'])

@app.route('/commonUnits', methods=['GET'])
def displayCommonUnits():
    return jsonify(tftDataDict['commonUnits'])

def getSummonerDataFromDB():
    load_dotenv()
    mongoUsername = os.getenv('MONGO_USERNAME')
    mongoPassword = os.getenv('MONGO_PASSWORD')
    mongoConnect = f'mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-vmp4h.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(mongoConnect)

    db = client['summoner_db']
    collection = db['summoners']

    # Get summoners using database
    summoners = []
    cursor = collection.find({})
    for document in cursor:
        accountInfo = document['accountInfo']
        matchIdList = document['matchIdList']
        matchInfoList = document['matchInfoList']
        unitsAndTraitsList = document['unitsAndTraitsList']
        summoner = Summoner(None, accountInfo, matchIdList, matchInfoList, unitsAndTraitsList)
        summoners.append(summoner)

    return summoners

def getDataFromDB():
    load_dotenv()
    mongoUsername = os.getenv('MONGO_USERNAME')
    mongoPassword = os.getenv('MONGO_PASSWORD')
    mongoConnect = f'mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-vmp4h.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(mongoConnect)

    db = client['tftstats_db']
    collection = db['tftstats']
    cursor = collection.find({})
    for document in cursor:
        tftDataDict = document
    return tftDataDict

# summoners = getSummonerDataFromDB()
tftDataDict = getDataFromDB()
