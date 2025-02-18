import requests
import time
from datetime import datetime

apikey = ""

funds = "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t"
ffex = "5ndLnEYqSFiA5yUFHo6LVZ1eWc6Rhh11K5CfJNkoHEPs"
raydium_add = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
pf_add = "39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg"
fournisseurs = [ffex, funds]

wallet_to_subscribe = []
wallet_to_unsubscribe = []
watching_wallet = []
checked = []
session = requests.Session()
session_pf = requests.Session()
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Origin': 'https://solscan.io',}    

def get_token_data(mint):
    params = {
        'address': mint,
        'page': '1',
        'page_size': '10',
        'exclude_amount_zero': 'false',
    }

    response = session.get('https://api-v2.solscan.io/v2/token/transfer', params=params, headers=headers)
    print(response.status_code)
    return response.json()["metadata"]['tokens'][mint]
    
def get_transfers(address, number, only_out = True):
    transfers = []
    params = {
        'address': address,
        'page_size': '100',
        'remove_spam': 'false',
        'exclude_amount_zero': 'false',
        'token': 'So11111111111111111111111111111111111111111',
    }
    if only_out:
        params["flow"]  = "out"
    for i in range(1, int(number/100) + 1):
        params['page'] = i
        response = session.get('https://api-v2.solscan.io/v2/account/transfer', params=params, headers=headers)
        transfers += response.json()['data']
    
    return transfers 
    {'block_id': 312686644, 'trans_id': 'HKTRPANMSL2mxAdXW2K5syYdCxRYcfQ7HdCA62oo5jWLVncWcmx9iaHNbargbRZKA71zDC5FxNxPBduWAjC9P9t', 'block_time': 1736348318, 'activity_type': 'ACTIVITY_SPL_TRANSFER', 'from_address': '5ndLnEYqSFiA5yUFHo6LVZ1eWc6Rhh11K5CfJNkoHEPs', 'from_token_account': '5ndLnEYqSFiA5yUFHo6LVZ1eWc6Rhh11K5CfJNkoHEPs', 'to_address': '8f7dpqAKEspG1UP78YqcJQQ66cdywim5cRP4Nb8UBBD7', 'to_token_account': '8f7dpqAKEspG1UP78YqcJQQ66cdywim5cRP4Nb8UBBD7', 'token_address': 'So11111111111111111111111111111111111111111', 'token_decimals': 9, 'amount': 10073347000, 'flow': 'out', 'value': 1990.8963010799998}

def get_filtered_addresses(transfers):
    addresses = []
    for transfer in transfers:
        if float(transfer['amount']) > 19000000000 and float(transfer['amount']) < 29900000000:
            addresses.append(transfer['to_address'])    
    return addresses
    
def check_add(address):
    data = get_transfers(address, 100, False)
    i = 2 if len(data) > 1 and data[1]["from_address"] == funds else 1 
    return False if len(data) > i else True

def is_rug2(mint):
    params = {
    'address': mint,
    'page_size': '100',
    'exclude_amount_zero': 'false',
    'from': raydium_add,
    'page': 1}
    response = session.get('https://api-v2.solscan.io/v2/token/transfer', params=params, headers=headers).json()["data"]
    if not response:
        return None
    response.reverse()
    price = 0
    for tx in response:
        if price == 0:
        # recuperer le prix lors de la première transaction
            amount = tx['amount']*10**-tx['token_decimals']
            price = tx['value']/amount
        if float(tx['amount']) > 100000000:
            return True, price
    return False, price
            
def get_migration_time(mint):
    response = session.get(
        f'https://api-v2.solscan.io/v2/token/transfer?address={mint}&page=1&page_size=10&exclude_amount_zero=false&from={pf_add}&to={raydium_add}',
        headers=headers,)
    if response.status_code == 200:
        if not response.json()['data']:
            return None
        return response.json()['data'][0]['block_time']
    else:
        print(response.content)
        
def get_last_price(mint):
    response = session.get(
        f'https://api-v2.solscan.io/v2/token/transfer?address={mint}&page=1&page_size=10&exclude_amount_zero=false',
        headers=headers,
    )
    if response.status_code == 200:        
        p =response.json()['data'][0]
        amount = p['amount']*10**-p['token_decimals']
        return p['value']/amount
        
def swap(side, mint, amount, slippage, priorityFee, pool):
    response = requests.post(url=f"https://pumpportal.fun/api/trade?api-key={apikey}", data={
        "action": side,             # "buy" or "sell"
        "mint": mint,      # contract address of the token you want to trade
        "amount": amount,            # amount of SOL or tokens to trade
        "denominatedInSol": "true" if side == 'buy' else 'false', # "true" if amount is amount of SOL, "false" if amount is number of tokens
        "slippage": slippage,              # percent slippage allowed
        "priorityFee": priorityFee,        # amount used to enhance transaction speed
        "pool": pool               # exchange to trade on. "pump" or "raydium"
    })
     
    data = response.json()           # Tx signature or error(s)
    return data
def maj_wallet_to_subscribe():
    global wallet_to_subscribe
    global wallet_to_unsubscribe
    i = 2500
    while True:
        print(f"maj du suivi de wallet {datetime.now().strftime('%H:%M:%S')}")
        news = []
        rm = []
        addresses = sum([get_transfers(address, i) for address in fournisseurs], [])
        first_sort = list(set(get_filtered_addresses(addresses) + watching_wallet))
        i = 200
        for address in first_sort:
            if address in checked:
                continue
            if check_add(address):
                if address not in watching_wallet:
                    news.append(address)
                    watching_wallet.append(address)
            else:
                checked.append(address)
                if address in watching_wallet:
                    watching_wallet.remove(address)
                    rm.append(address)
        wallet_to_subscribe += news
        wallet_to_unsubscribe += rm
        time.sleep(15*60)

def send_message(message):
    # URL de l'API Telegram
    url = f"https://api.telegram.org/bot7748028669:AAE82F36LbbuoYDkjxQRpQaCElxwYbgkeA0/sendMessage"

    # Paramètres de la requête
    params = {
        "chat_id": 1915713185,
        "text": message
    }

    # Envoi de la requête
    response = requests.get(url, params=params)
if __name__ == "__main__":
    mint = "644MryX1MXBNjA8QEUNeQ5HSEVZZqGRzPdiLz4EBpump"
    print(get_last_price(mint)) 
    # news = []
    # addresses = sum([get_transfers(address, 1000) for address in fournisseurs], [])
    # first_sort = list(set(get_filtered_addresses(addresses)))
    # for address in first_sort:
        # if check_add(address):
            # if address not in watching_wallet:
                # news.append(address)
    # print(news)
