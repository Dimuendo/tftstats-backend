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
    # Get the comp stats
    top10CompStats = getCompStats(summoners)

    # Get the placement for each item, unit, and trait
    placementDict = getPlacementDictionaries(summoners)

    # Find the items which have the best top4 rate and win rate
    itemPercentagesAndCommonUnits = getItemPercentages(placementDict)
    itemPercentages = itemPercentagesAndCommonUnits['itemStats']
    commonUnits = itemPercentagesAndCommonUnits['commonUnits']

    # Find the win rate and top 4 rate of each unit
    unitPercentages = getUnitPercentages(placementDict)

    # Find the win rate and top 4 rate of each trait
    traitPercentages = getTraitPercentages(placementDict)

    # Find the most common items on each unit and the most common carries
    # Carries => Two or more items when game ends
    unitItems = getUnitItems(summoners)
    # mostCommonCarries = sorted(unitItems['unitCarryCount'].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    commonItems = {}
    for character_id, itemDict in unitItems['unitItems'].items():
        commonItems[character_id] = sorted(itemDict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    return {
        'compStats': top10CompStats,
        'itemPercentages': itemPercentages,
        'unitPercentages': unitPercentages,
        'traitPercentages': traitPercentages['total'],
        'commonItems': commonItems,
        'commonUnits': commonUnits,
    }
