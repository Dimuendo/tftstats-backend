import json
from collections import Counter

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

# Load traits
with open('set3/traits.json') as f:
    traits = json.load(f)
traitNames = {}
for trait in traits:
    traitNames[trait['key']] = trait['name']

def extractUnits(comp):
    unitList = []
    for unit in comp:
        unitList.append(unit['character_id'])
    return sorted(unitList)

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
