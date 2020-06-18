import json
import time
import requests

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
