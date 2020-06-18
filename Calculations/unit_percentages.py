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