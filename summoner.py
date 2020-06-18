from RiotAPI.riot_api_helpers import requestRiotAPI
from dotenv import load_dotenv
import os

class Summoner():
    def __init__(self, summonerName=None, accountInfo=None, matchIdList=None, matchInfoList=None, unitsAndTraitsList=None):
        API_KEY = os.getenv('API_KEY')

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