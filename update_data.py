from summoner import Summoner
from RiotAPI.riot_api_helpers import requestRiotAPI
import os
from dotenv import load_dotenv
import pymongo
from tftcomps import getData

def getTopPlayers(numPlayers):
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    topPlayers = []
    numPlayersLeft = numPlayers

    # Get the challenger players
    challengerRequest = f'https://na1.api.riotgames.com/tft/league/v1/challenger?api_key={API_KEY}'
    challengerResponse = requestRiotAPI(challengerRequest)
    challengerPlayers = challengerResponse.json()['entries']
    if len(challengerPlayers) != 0:
        challengerPlayers = sorted(challengerPlayers, key = lambda i: i['leaguePoints'], reverse=True)
        numPlayersLeft = numPlayersLeft - len(challengerPlayers)
        topPlayers += challengerPlayers

    if numPlayersLeft <= 0:
        return topPlayers[:numPlayers]

    # Get the grandmaster players
    grandmasterRequest = f'https://na1.api.riotgames.com/tft/league/v1/grandmaster?api_key={API_KEY}'
    grandmasterResponse = requestRiotAPI(grandmasterRequest)
    grandmasterPlayers = grandmasterResponse.json()['entries']
    if len(grandmasterPlayers) != 0:
        grandmasterPlayers = sorted(grandmasterPlayers, key = lambda i: i['leaguePoints'], reverse=True)
        numPlayersLeft = numPlayersLeft - len(grandmasterPlayers)
        topPlayers += grandmasterPlayers

    if numPlayersLeft <= 0:
        return topPlayers[:numPlayers]

    # Get the masters players
    masterRequest = f'https://na1.api.riotgames.com/tft/league/v1/master?api_key={API_KEY}'
    masterResponse = requestRiotAPI(masterRequest)
    masterPlayers = masterResponse.json()['entries']
    if len(masterPlayers) != 0:
        masterPlayers = sorted(masterPlayers, key = lambda i: i['leaguePoints'], reverse=True)
        numPlayersLeft = numPlayersLeft - len(masterPlayers)
        topPlayers += masterPlayers

    if numPlayersLeft <= 0:
        return topPlayers[:numPlayers]

    # Get the diamond, players
    tiers = ['I', 'II', 'III', 'IV']
    for tier in tiers:
        diamondRequest = f'https://na1.api.riotgames.com/tft/league/v1/entries/DIAMOND/{tier}?page=1&api_key={API_KEY}'
        diamondResponse = requestRiotAPI(diamondRequest)
        diamondPlayers = diamondResponse.json()
        if len(diamondPlayers) != 0:
            diamondPlayers = sorted(diamondPlayers, key = lambda i: i['leaguePoints'], reverse=True)
            numPlayersLeft = numPlayersLeft - len(diamondPlayers)
            topPlayers += diamondPlayers

        if numPlayersLeft <= 0:
            return topPlayers[:numPlayers]

    return topPlayers

def putSummonersInDB():
    # Get the top n players
    numPlayers = 1000
    topPlayers = getTopPlayers(numPlayers)

    # Get summoners by requesting Riot API
    count = 1
    summoners = []
    for player in topPlayers:
        try:
            summoner = Summoner(player['summonerName'])
        except:
            continue
        summoners.append(summoner)
        print(f'Summoners: {count}/{len(topPlayers)}')
        count += 1

    # Connect to the MongoDB database
    load_dotenv()
    mongoUsername = os.getenv('MONGO_USERNAME')
    mongoPassword = os.getenv('MONGO_PASSWORD')
    mongoConnect = f'mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-vmp4h.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(mongoConnect)

    db = client['summoner_db']
    oldCollection = db['summoners']
    oldCollection.drop()
    collection = db['summoners']

    # Put summoners in database
    for summoner in summoners:
        summonerName = summoner.accountInfo['name']
        summonerCollection = {
            '_id': summonerName,
            'accountInfo': summoner.accountInfo,
            'matchIdList': summoner.matchIdList,
            'matchInfoList': summoner.matchInfoList,
            'unitsAndTraitsList': summoner.unitsAndTraitsList
        }
        summonerInsertion = collection.insert_one(summonerCollection)

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

def putStatsInDB():
    summoners = getSummonerDataFromDB()

    # Get the stats for the summoners in the database
    print('Calculating data')
    data = getData(summoners)

    # Connect to the MongoDB database
    load_dotenv()
    mongoUsername = os.getenv('MONGO_USERNAME')
    mongoPassword = os.getenv('MONGO_PASSWORD')
    mongoConnect = f'mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-vmp4h.mongodb.net/test?retryWrites=true&w=majority'
    client = pymongo.MongoClient(mongoConnect)

    db = client['summoner_db']
    collection = db['summoners']

    # Put the stats data in the database
    print('Putting stats in database')
    db = client['tftstats_db']
    oldCollection = db['tftstats']
    oldCollection.drop()
    collection = db['tftstats']
    dataInsertion = collection.insert_one(data) 
