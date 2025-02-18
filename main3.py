from tools import *
import asyncio
import websockets
import json
import threading
from datetime import datetime


bet = 0.12
watching_token = {}

async def subscribe():
    uri = "wss://pumpportal.fun/api/data"
    while True:
        print("lancement while true principal")
        try:
            async with websockets.connect(uri) as websocket:
                print("WebSocket connection established.")
                      # Subscribing to token creation events
                payload = {"method": "subscribeRaydiumLiquidity",}
                await websocket.send(json.dumps(payload))
                if watching_wallet:
                    payload = {
                        "method": "subscribeAccountTrade",
                        "keys": watching_wallet
                        }
                    await websocket.send(json.dumps(payload))

                async def handle_subscriptions():
                    while True:
                        # Gestion des abonnements
                        if wallet_to_subscribe:
                            payload = {
                                "method": "subscribeAccountTrade",
                                "keys": wallet_to_subscribe
                            }
                            await websocket.send(json.dumps(payload))
                            print(f"Subscribed to: {wallet_to_subscribe} {datetime.now().strftime('%H:%M:%S')}")
                            wallet_to_subscribe.clear()

                        # Gestion des désabonnements
                        if wallet_to_unsubscribe:
                            payload = {
                                "method": "unsubscribeAccountTrade",
                                "keys": wallet_to_unsubscribe
                            } 
                            await websocket.send(json.dumps(payload))
                            print(f"Unsubscribed from: {wallet_to_unsubscribe} {datetime.now().strftime('%H:%M:%S')}")
                            wallet_to_unsubscribe.clear()
                        await asyncio.sleep(5)
                async def handle_messages():
                    async for message in websocket:
                        data = json.loads(message)
                        on_message(data)

                # Exécuter les deux tâches simultanément
                await asyncio.gather(handle_subscriptions(), handle_messages())
        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
            print("Connection lost. Retrying...")
            await asyncio.sleep(5)  # Attendre un peu avant de réessayer
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying...")
            await asyncio.sleep(5)

def watch_token(mint, data):
    
    t = time.time()
    while True:
        if not watching_token.get(mint, False):
            if time.time()>t +900:
                return
            time.sleep(0.5)
        else:
            break
    r, price = is_rug2(mint)
    while r is None:
        r, price = is_rug2(mint)
        time.sleep(0.5)
    if r:
        time.sleep(60*5)
        if get_last_price(mint) < price:
            return
    # response = swap("buy", mint, bet, 30, 0.006, data["pool"])
    send_message(f"buy du mint {mint}.\nmarketcap: {data['price_usdt']*(10**9)}$\nhttps://dexscreener.com/solana/{mint}")
    
    return

def on_message(data):
    global watching_token

    side = data.get("txType", None)
    address = data.get("traderPublicKey", None)
    
    if side == 'addLiquidity':
        mint = data['mint']
        if mint in watching_token:
            watching_token[mint] = True
        return    
    
    if address:
        watching_wallet.remove(address)
        wallet_to_unsubscribe.append(address)
 
    if side not in ["create"] or data["solAmount"] != 15:
        print(data)
        return
    
    
    mint = data["mint"]
    print(f"{side} {mint}")
    send_message(f"{side} {mint}")
    watching_token[mint] = False
    watch_token(mint, data)
    
def main_maj():
    try:    
        maj_wallet_to_subscribe()
    except Exception as e:
        print(f"Unexpected error in maj_wallet_to_subscribe: {e}. Retrying...")
        time.sleep(5)


response = requests.get('https://api.ipify.org?format=json')
ip_data = response.json()
send_message(ip_data['ip'])

threading.Thread(target=main_maj, daemon=True).start()
asyncio.get_event_loop().run_until_complete(subscribe())
