import pandas as pd
import requests
import time
fournisseur = "5ndLnEYqSFiA5yUFHo6LVZ1eWc6Rhh11K5CfJNkoHEPs"

wallet_to_subscribe = []
wallet_to_unsubscribe = []
watching_wallet = []
checked = []
def get_transfer(address, only_out = False):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',}
    params = {'address': address, 'token': 'So11111111111111111111111111111111111111111'}
    if only_out:
        params['flow']='out'
    response = requests.get('https://api-v2.solscan.io/v2/account/transfer/export', params=params, headers=headers)
    lines = response.text.strip().split("\n")
    df = pd.DataFrame([line.split(",") for line in lines[1:]], columns=lines[0].split(","))
    return df
    
import pandas as pd

def get_filtered_addresses(dataframe):
    """
    Récupère les adresses des lignes de la colonne "To" 
    où la colonne "Amount" est comprise entre 20 et 30, "Flow" est "out",
    et "Action" est "TRANSFER".

    :param dataframe: DataFrame Pandas contenant les données
    :return: Liste des adresses correspondantes
    """
    # Filtrer les lignes selon les conditions
    dataframe['Amount'] = pd.to_numeric(dataframe['Amount'], errors='coerce')
    filtered_rows = dataframe[
        (dataframe['Amount'] * 10**-9 >= 20) &
        (dataframe['Amount'] * 10**-9 <= 30) &
        (dataframe['Flow'] == 'out') &
        (dataframe['Action'] == 'TRANSFER')
    ]
    
    # Récupérer les adresses dans la colonne "To"
    addresses = list(set(filtered_rows['To'].tolist()))
    
    return addresses
    
def check_add(address):
    data = get_transfer(address)
    return False if len(data) > 1 else True

def maj_wallet_to_subscribe():    
    while True:
        df = get_transfer(fournisseur, only_out=True)
        print("get dataframe")
        first_sort = get_filtered_addresses(df)
        print("first sort done")
        for address in first_sort:
            if address in checked:
                continue
            if check_add(address):
                wallet_to_subscribe.append(address)
            elif address in watching_wallet:
                watching_wallet.pop(address)
                wallet_to_unsubscribe.append(address)
                checked.append(address)
            else:
                checked.append(address)
        time.sleep(3600*0.5)

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