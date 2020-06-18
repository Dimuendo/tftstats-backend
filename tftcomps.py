import requests
import urllib.request
from pprint import pprint
from collections import Counter
import json
import os
import time
import plotly.graph_objects as go
import plotly
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup as bs
import pymongo
import dns
import sys
import flask
from flask import request, jsonify
from operator import itemgetter
import math

RESPONSES = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Data not found',
    405: 'Method not allowed',
    415: 'Unsupported media type',
    429: 'Rate limit exceeded',
    500: 'Internal server error',
    502: 'Bad gateway',
    503: 'Service unavailabe',
    504: 'Gateway timeout'
}

RESPONSES = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Data not found',
    405: 'Method not allowed',
    415: 'Unsupported media type',
    429: 'Rate limit exceeded',
    500: 'Internal server error',
    502: 'Bad gateway',
    503: 'Service unavailabe',
    504: 'Gateway timeout'
}

API_KEY = os.getenv('API_KEY')

# Load items
with open('set3/items.json') as f:
    items = json.load(f)
itemDict = {}
for item in items:
    itemDict[item['id']] = item['name']

# Load traits
with open('set3/traits.json') as f:
    traits = json.load(f)
traitNames = {}
for trait in traits:
    traitNames[trait['key']] = trait['name']

# Load champions
with open('set3/champions.json') as f:
    champions = json.load(f)

#################################
### Riot API Helper Functions ###
#################################

# Sleep for the given number of seconds but show a "progress bar" during the sleep
def sleepWithProgress(seconds):
    fullProgressSpaces = '-' * seconds
    fullProgress = f'|{fullProgressSpaces}|'
    print(fullProgress)
    print('|', end = '')
    for i in range(seconds):
        time.sleep(1)
        print('=', end = '')
    print('|')

# Request the riot api and output the status if the request fails
def requestRiotAPI(request, attempts=0):
    if attempts == 5:
        print('Max attempts reached - ending')
        return None
    response = requests.get(request)
    if response.status_code == 200:
        return response
    elif response.status_code == 429:
        print('Waiting for the rate limit to reset')
        sleepWithProgress(130)
        return requestRiotAPI(request) 
    else:
        print(RESPONSES[response.status_code])
        print(response)
        return requestRiotAPI(request, attempts + 1) 

def getTopPlayers(numPlayers):
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

class Summoner():
    def __init__(self, summonerName=None, accountInfo=None, matchIdList=None, matchInfoList=None, unitsAndTraitsList=None):
        # Get the account info for the given summoner name
        if accountInfo is None:
            accountRequest = f'https://na1.api.riotgames.com/tft/summoner/v1/summoners/by-name/{summonerName}?api_key={API_KEY}'
            accountResponse = requestRiotAPI(accountRequest)
            self.accountInfo = accountResponse.json()
        else:
            self.accountInfo = accountInfo

        # Get the match ids for the summoners math history
        if matchIdList is None:
            puuid = self.accountInfo['puuid']
            numMatches = 20
            matchIdsRequest = f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={numMatches}&api_key={API_KEY}'
            matchIdsResponse = requestRiotAPI(matchIdsRequest)
            self.matchIdList = matchIdsResponse.json()
        else:
            self.matchIdList = matchIdList

        # Get the match info for each match in the matchIdList
        if matchInfoList is None:
            self.matchInfoList = []
            for matchId in self.matchIdList:
                matchInfoRequest = f'https://americas.api.riotgames.com/tft/match/v1/matches/{matchId}?api_key={API_KEY}'
                matchInfoResponse = requestRiotAPI(matchInfoRequest)
                matchInfo = matchInfoResponse.json()
                self.matchInfoList.append(matchInfo)
        else:
            self.matchInfoList = matchInfoList

        # Get the units and traits for each game for the given summoner
        if unitsAndTraitsList is None:
            self.unitsAndTraitsList = []
            for matchInfo in self.matchInfoList:
                for participant in matchInfo['info']['participants']:
                    if participant['puuid'] != self.accountInfo['puuid']:
                        continue
                    else:
                        placement = participant['placement']
                        matchTraits = participant['traits']
                        matchUnits = participant['units']
                        self.unitsAndTraitsList.append({
                            'placement': placement,
                            'traits': matchTraits,
                            'units': matchUnits
                        })
                        break
        else:
            self.unitsAndTraitsList = unitsAndTraitsList

def getPlacementDictionaries(summoners):
    unitDict = {}
    traitDict = {'major': {}, 'minor': {}, 'total': {}}
    itemDict = {}
    for summoner in summoners:
        # Get dictionary of units and their respective placings
        for unitsAndTraits in summoner.unitsAndTraitsList:
            # Get the placement for each unit and item
            for unit in unitsAndTraits['units']:
                if unit['character_id'] in unitDict:
                    unitDict[unit['character_id']].append(unitsAndTraits['placement'])
                else:
                    unitDict[unit['character_id']] = [unitsAndTraits['placement']]
                
                for item in unit['items']:
                    if item in itemDict:
                        itemDict[item].append({'placement': unitsAndTraits['placement'], 'character': unit['character_id']})
                    else:
                        itemDict[item] = [{'placement': unitsAndTraits['placement'], 'character': unit['character_id']}]

            # Get the placement for each trait
            for trait in unitsAndTraits['traits']:
                if trait['tier_current'] == 0:
                    continue
                    
                isMajorTrait = False
                if trait['tier_total'] == 1 or trait['tier_current'] >= 2:
                    isMajorTrait = True

                if trait['name'] in traitDict['total']:
                    traitDict['total'][trait['name']].append(unitsAndTraits['placement'])
                else:
                    traitDict['total'][trait['name']] = [unitsAndTraits['placement']]

                if isMajorTrait:
                    if trait['name'] in traitDict['major']:
                        traitDict['major'][trait['name']].append(unitsAndTraits['placement'])
                    else:
                        traitDict['major'][trait['name']] = [unitsAndTraits['placement']]
                else:
                    if trait['name'] in traitDict['minor']:
                        traitDict['minor'][trait['name']].append(unitsAndTraits['placement'])
                    else:
                        traitDict['minor'][trait['name']] = [unitsAndTraits['placement']]
    
    return {'items': itemDict, 'units': unitDict, 'traits': traitDict}

def getUnitItems(summoners):
    unitItemDict = {}
    unitCarryDict = {}
    for summoner in summoners:
        for unitsAndTraits in summoner.unitsAndTraitsList:
            for unit in unitsAndTraits['units']:
                for item in unit['items']:
                    if unit['character_id'] in unitItemDict:
                        if item in unitItemDict[unit['character_id']]:
                            unitItemDict[unit['character_id']][item] += 1
                        else:
                            unitItemDict[unit['character_id']][item] = 1
                    else:
                        unitItemDict[unit['character_id']] = {item: 1}

                if len(unit['items']) >= 2:
                    if unit['character_id'] in unitCarryDict:
                            unitCarryDict[unit['character_id']] += 1
                    else:
                        unitCarryDict[unit['character_id']] = 1
    return {'unitItems': unitItemDict, 'unitCarryCount': unitCarryDict}

# def getComps(summoners):
#     compDict = {}
#     for summoner in summoners:
#         for unitsAndTraits in summoner.unitsAndTraitsList:
#             for trait in unitsAndTraits['traits']:
#                 if trait['tier_current'] == 0:
#                     continue
#                 if trait['tier_current'] > 0:
#                     if trait['name'] in compDict:
#                         compDict[trait['name']].append(unitsAndTraits['units'].copy())
#                     else:
#                         compDict[trait['name']] = [unitsAndTraits['units'].copy()]
#     return compDict

def extractUnits(comp):
    unitList = []
    for unit in comp:
        unitList.append(unit['character_id'])
    return sorted(unitList)

# def getCompPlayRates(comps):
#     compPlayRates = {}
#     compPlayRatesByTrait = {}
#     top5CompsByTrait = {}
#     for trait, comp in comps.items():
#         compPlayRatesByTrait[trait] = {}
#         top5CompsByTrait[trait] = {}

#     for trait, compList in comps.items():
#         for comp in compList:
#             unitList = extractUnits(comp)
#             strUnitList = ','.join(unitList)
#             if strUnitList in compPlayRates:
#                 compPlayRates[strUnitList] += 1
#             else:
#                 compPlayRates[strUnitList] = 1
#             if strUnitList in compPlayRatesByTrait[trait]:
#                 compPlayRatesByTrait[trait][strUnitList] += 1
#             else:
#                 compPlayRatesByTrait[trait][strUnitList] = 1

#     for trait, compDict in compPlayRatesByTrait.items():
#         playRates = Counter(compDict)
#         top5CompsByTrait[trait] = playRates.most_common(5)

#     playRates = Counter(compPlayRates)
#     top10Comps = playRates.most_common(10)

#     return {'top5ByTrait': top5CompsByTrait, 'top10Comps': top10Comps}

def compIsSubset(unitLists, currUnitList):
    for unitList in unitLists:
        if (all(unit in unitList for unit in currUnitList)) and (unitList != currUnitList):
            return unitList
    return []

def getCompName(traits):
    traitList = []
    for trait in traits:
        if trait['tier_current'] >= 1 and trait['num_units'] >= 3:
            traitList.append(traitNames[trait['name']])
    return ', '.join(traitList)

def getCompPercentages(placements):
    compPercentages = {
        'totalTimesPlayed': len(placements),
        'totalWins': 0,
        'totalTop4': 0,
        'totalBottom4': 0
    }
    for placement in placements:
        if placement == 1:
            compPercentages['totalWins'] += 1
            compPercentages['totalTop4'] += 1
        elif placement >= 4:
            compPercentages['totalTop4'] += 1
        else:
            compPercentages['totalBottom4'] += 1
    compPercentages['winPercentage'] = compPercentages['totalWins'] / compPercentages['totalTimesPlayed']
    compPercentages['top4Percentage'] = compPercentages['totalTop4'] / compPercentages['totalTimesPlayed']
    compPercentages['bottom4Percentage'] = compPercentages['totalBottom4'] / compPercentages['totalTimesPlayed']
    return compPercentages

def getCompStats(summoners):
    compPlayRate = {}
    compStats = {}
    for summoner in summoners:
        for unitsAndTraits in summoner.unitsAndTraitsList:
            unitList = extractUnits(unitsAndTraits['units'])
            strUnitList = ','.join(unitList)
            if strUnitList in compStats:
                compStats[strUnitList]['placements'].append(unitsAndTraits['placement'])
                compPlayRate[strUnitList] += 1
            else:
                compStats[strUnitList] = {}
                compStats[strUnitList]['placements'] = [unitsAndTraits['placement']]
                compStats[strUnitList]['traits'] = unitsAndTraits['traits'].copy()
                compStats[strUnitList]['units'] = unitsAndTraits['units'].copy()
                compPlayRate[strUnitList] = 1
            
    playRates = Counter(compPlayRate)
    top10Comps = playRates.most_common(10)
    top10CompsStats = {}
    for compPlayRates in top10Comps:
        strUnitList = compPlayRates[0]
        compName = getCompName(compStats[strUnitList]['traits'])
        compPercentages = getCompPercentages(compStats[strUnitList]['placements'])
        top10CompsStats[strUnitList] = compStats[strUnitList].copy()
        top10CompsStats[strUnitList]['compName'] = compName
        top10CompsStats[strUnitList]['winPercentage'] = compPercentages['winPercentage']
        top10CompsStats[strUnitList]['top4Percentage'] = compPercentages['top4Percentage']
        top10CompsStats[strUnitList]['bottom4Percentage'] = compPercentages['bottom4Percentage']

    return top10CompsStats

def getUnitPercentages(placementDictionary):
    unitStatsDict = {}
    for unit, placements in placementDictionary['units'].items():
        unitStats = {
            'totalTimesPlayed': len(placements),
            'totalWins': 0,
            'totalTop4': 0,
            'totalBottom4': 0
        }
        for placement in placements:
            if placement == 1:
                unitStats['totalWins'] += 1
                unitStats['totalTop4'] += 1
            elif placement >= 4:
                unitStats['totalTop4'] += 1
            else:
                unitStats['totalBottom4'] += 1
        unitStats['winPercentage'] = unitStats['totalWins'] / unitStats['totalTimesPlayed']
        unitStats['top4Percentage'] = unitStats['totalTop4'] / unitStats['totalTimesPlayed']
        unitStats['bottom4Percentage'] = unitStats['totalBottom4'] / unitStats['totalTimesPlayed']
        unitStatsDict[unit] = unitStats
    return unitStatsDict

def getItemPercentages(placementDictionary):
    itemStatsDict = {}
    commonUnits = {}
    for item, placementsAndUnits in placementDictionary['items'].items():
        itemStats = {
            'itemName': itemDict[item],
            'totalTimesPlayed': len(placementsAndUnits),
            'totalWins': 0,
            'totalTop4': 0,
            'totalBottom4': 0
        }
        commonUnits[item] = {}
        for placementAndUnit in placementsAndUnits:
            placement = placementAndUnit['placement']
            character = placementAndUnit['character']
            if placement == 1:
                itemStats['totalWins'] += 1
                itemStats['totalTop4'] += 1
            elif placement >= 4:
                itemStats['totalTop4'] += 1
            else:
                itemStats['totalBottom4'] += 1

            if character in commonUnits[item]:
                commonUnits[item][character] += 1
            else:
                commonUnits[item][character] = 1
        itemStats['winPercentage'] = itemStats['totalWins'] / itemStats['totalTimesPlayed']
        itemStats['top4Percentage'] = itemStats['totalTop4'] / itemStats['totalTimesPlayed']
        itemStats['bottom4Percentage'] = itemStats['totalBottom4'] / itemStats['totalTimesPlayed']
        itemStatsDict[item] = itemStats
    for item, units in commonUnits.items():
        unitItemCounter = Counter(units)
        commonUnits[item] = unitItemCounter.most_common(3)
    return {'itemStats': itemStatsDict, 'commonUnits': commonUnits}

# Major trait => Reached 2'nd tier in comp
# Minor trait => Only reached 1'st tier
def getTraitPercentages(placementDictionary):
    traitStatsDict = {'major': {}, 'minor': {}, 'total': {}}
    for traitTier, traitPlacements in placementDictionary['traits'].items():
        for trait, placements in placementDictionary['traits'][traitTier].items():
            traitStats = {
                'totalTimesPlayed': len(placements),
                'totalWins': 0,
                'totalTop4': 0,
                'totalBottom4': 0
            }
            for placement in placements:
                if placement == 1:
                    traitStats['totalWins'] += 1
                    traitStats['totalTop4'] += 1
                elif placement >= 4:
                    traitStats['totalTop4'] += 1
                else:
                    traitStats['totalBottom4'] += 1
            traitStats['winPercentage'] = traitStats['totalWins'] / traitStats['totalTimesPlayed']
            traitStats['top4Percentage'] = traitStats['totalTop4'] / traitStats['totalTimesPlayed']
            traitStats['bottom4Percentage'] = traitStats['totalBottom4'] / traitStats['totalTimesPlayed']
            traitStatsDict[traitTier][trait] = traitStats
    return traitStatsDict

def getSummonerDataFromDB():
    from dotenv import load_dotenv
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

def getData(numPlayers, updateData):
    if updateData:
        # Get the top n players
        topPlayers = getTopPlayers(numPlayers)
        # with open('top_200.txt', 'w') as file:
        #     file.write(json.dumps(topPlayers, indent=4))

        # Get summoners by requesting Riot API
        count = 1
        summoners = []
        for player in topPlayers:
            summoner = Summoner(player['summonerName'])
            summoners.append(summoner)
            print(f'Summoners: {count}/{len(topPlayers)}')
            count += 1
    else:
        summoners = getSummonerDataFromDB()

    # Get the comp stats
    top10CompStats = getCompStats(summoners)
    # with open('compStats.txt', 'w') as file:
    #     file.write(json.dumps(top10CompStats, indent=4))

    # Get the placement for each item, unit, and trait
    placementDict = getPlacementDictionaries(summoners)
    # with open('placement_dicts.txt', 'w') as file:
    #     file.write(json.dumps(placementDict, indent=4))

    # Find the items which have the best top4 rate and win rate
    itemPercentagesAndCommonUnits = getItemPercentages(placementDict)
    itemPercentages = itemPercentagesAndCommonUnits['itemStats']
    commonUnits = itemPercentagesAndCommonUnits['commonUnits']
    # bestWinRateItems = sorted(itemPercentages, key=lambda i: i['winPercentage'], reverse=True)
    # bestTop4Items = sorted(itemPercentages, key=lambda i: i['top4Percentage'], reverse=True)

    # Find the win rate and top 4 rate of each unit
    unitPercentages = getUnitPercentages(placementDict)
    # bestWinRateUnits = sorted(unitPercentages, key=lambda i: i['winPercentage'], reverse=True)
    # bestTop4Units = sorted(unitPercentages, key=lambda i: i['top4Percentage'], reverse=True)

    # Find the win rate and top 4 rate of each trait
    traitPercentages = getTraitPercentages(placementDict)
    # # Major Traits
    # bestWinRateMajorTraits = sorted(traitPercentages['major'], key=lambda i: i['winPercentage'], reverse=True)
    # bestTop4MajorTraits = sorted(traitPercentages['major'], key=lambda i: i['top4Percentage'], reverse=True)
    # # Minor Traits
    # bestWinRateMajorTraits = sorted(traitPercentages['minor'], key=lambda i: i['winPercentage'], reverse=True)
    # bestTop4MajorTraits = sorted(traitPercentages['minor'], key=lambda i: i['top4Percentage'], reverse=True)
    # bestWinRateTraits = sorted(traitPercentages['total'], key=lambda i: i['winPercentage'], reverse=True)
    # bestTop4Traits = sorted(traitPercentages['total'], key=lambda i: i['top4Percentage'], reverse=True)

    # Find the most common items on each unit and the most common carries
    # Carries => Two or more items when game ends
    unitItems = getUnitItems(summoners)
    mostCommonCarries = sorted(unitItems['unitCarryCount'].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    commonItems = {}
    for character_id, itemDict in unitItems['unitItems'].items():
        commonItems[character_id] = sorted(itemDict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    # with open('common_carries.txt', 'w') as file:
    #     file.write(json.dumps(mostCommonCarries, indent=4))

    # with open('common_items.txt', 'w') as file:
    #     file.write(json.dumps(commonItems, indent=4))

    return {
        'summoners': summoners,
        'compStats': top10CompStats,
        'placementDict': placementDict,
        'itemPercentages': itemPercentages,
        'unitPercentages': unitPercentages,
        'traitPercentages': traitPercentages['total'],
        'commonItems': commonItems,
        'commonUnits': commonUnits,
    }

def runFlaskAPI(tftDataDict):
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

    app.run(threaded=True, port=5000)

if __name__ == '__main__':
    tftDataDict = getData(numPlayers=1000, updateData=False)
    runFlaskAPI(tftDataDict)
