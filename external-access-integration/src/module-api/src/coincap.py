import requests

session = requests.Session()
URL = 'https://api.coincap.io/v2'

def get_coin_story(coin, start, end):
    url = f"{URL}/assets/{coin}/history"
    response = session.get(url, params={"interval": 'd1', "start": start, "end": end})
    return response.json()['data']

def get_crypto_coins():
    url = f"{URL}/rates"
    response = session.get(url)
    all_coins = response.json()['data']
    crypto_coins = []
    for coin in all_coins:
        if coin["type"] == 'crypto':
            crypto_coins.append(coin)
    return crypto_coins