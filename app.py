import flask
from tftcomps import getData
from flask import request, jsonify
from summoner import Summoner
import pymongo
from dotenv import load_dotenv
from flask_cors import CORS
import os

app = flask.Flask(__name__)
CORS(app)

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

@app.route('/unitStats', methods=['GET'])
def displayUnitStats():
    unitPercentages = tftDataDict['unitPercentages']
    commonItems = tftDataDict['commonItems']
    return jsonify({'unitPercentages': unitPercentages, 'commonItems': commonItems})

@app.route('/itemStats', methods=['GET'])
def displayitemStats():
    itemPercentages = tftDataDict['itemPercentages']
    commonUnits = tftDataDict['commonUnits']
    return jsonify({'itemPercentages': itemPercentages, 'commonUnits': commonUnits})

@app.route('/updateData')
def updateData():
    global tftDataDict
    tftDataDict = getDataFromDB()

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

tftDataDict = getDataFromDB()
