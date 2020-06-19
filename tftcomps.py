import json
import os
import pymongo
from summoner import Summoner
from dotenv import load_dotenv
from Calculations.comp_percentages import getCompStats
from Calculations.unit_percentages import getUnitPercentages, getUnitItems
from Calculations.item_percentages import getItemPercentages
from Calculations.trait_percentages import getTraitPercentages

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

def getData(summoners):
    # if updateData:
        # # Get the top n players
        # topPlayers = getTopPlayers(numPlayers)
        # # with open('top_200.txt', 'w') as file:
        # #     file.write(json.dumps(topPlayers, indent=4))

        # # Get summoners by requesting Riot API
        # count = 1
        # summoners = []
        # for player in topPlayers:
        #     summoner = Summoner(player['summonerName'])
        #     summoners.append(summoner)
        #     print(f'Summoners: {count}/{len(topPlayers)}')
        #     count += 1
    # else:
    #     summoners = getSummonerDataFromDB()

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
    # mostCommonCarries = sorted(unitItems['unitCarryCount'].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    commonItems = {}
    for character_id, itemDict in unitItems['unitItems'].items():
        commonItems[character_id] = sorted(itemDict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    # with open('common_carries.txt', 'w') as file:
    #     file.write(json.dumps(mostCommonCarries, indent=4))

    # with open('common_items.txt', 'w') as file:
    #     file.write(json.dumps(commonItems, indent=4))

    return {
        'compStats': top10CompStats,
        'itemPercentages': itemPercentages,
        'unitPercentages': unitPercentages,
        'traitPercentages': traitPercentages['total'],
        'commonItems': commonItems,
        'commonUnits': commonUnits,
    }

# def getSummonerDataFromDB():
#     load_dotenv()
#     mongoUsername = os.getenv('MONGO_USERNAME')
#     mongoPassword = os.getenv('MONGO_PASSWORD')
#     mongoConnect = f'mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-vmp4h.mongodb.net/test?retryWrites=true&w=majority'
#     client = pymongo.MongoClient(mongoConnect)

#     db = client['summoner_db']
#     collection = db['summoners']

#     # Get summoners using database
#     summoners = []
#     cursor = collection.find({})
#     for document in cursor:
#         accountInfo = document['accountInfo']
#         matchIdList = document['matchIdList']
#         matchInfoList = document['matchInfoList']
#         unitsAndTraitsList = document['unitsAndTraitsList']
#         summoner = Summoner(None, accountInfo, matchIdList, matchInfoList, unitsAndTraitsList)
#         summoners.append(summoner)

#     db = client['tftstats_db']
#     collection = db['tftstats']
#     data = getData(summoners)
#     with open('test.txt', 'w') as file:
#         file.write(json.dumps(data, indent=4))
#     dataInsertion = collection.insert_one(data)

#     return summoners

# summoners = getSummonerDataFromDB()
