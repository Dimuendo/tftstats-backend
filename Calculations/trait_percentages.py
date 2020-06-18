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