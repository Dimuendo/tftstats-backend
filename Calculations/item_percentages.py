import json
from collections import Counter

# Load items
with open('set3/items.json') as f:
    items = json.load(f)
itemDict = {}
for item in items:
    itemDict[item['id']] = item['name']

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
