from tools import *
import asyncio
import websockets
import json
import threading
from datetime import datetime

async def subscribe():
    uri = "wss://pumpportal.fun/api/data"
    while True:
        print("lancement while true principal")
        try:
            async with websockets.connect(uri) as websocket:
                print("WebSocket connection established.")
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
                        print(f'{datetime.now().strftime("%H:%M:%S")}:{round((time.time()-int(time.time()))*100)}')
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
        ts = get_migration_time(mint)
        if ts:
            time.sleep(0.7)
            if is_rug(mint, ts):
                break
        time.sleep(0.3)
        
    send_message(f"buy suy du mint {mint}.\nmarketcap: {data['price_usdt']*(10**9)}$\nhttps://dexscreener.com/solana/{mint}")
    response = swap("buy", mint, bet, 30, 0.006, data["pool"])
    
    return
    # price = get_token_data(mint)["price_usdt"]
    # if price > 10**(-4):
    # send_message(f"buy suy du mint {mint}.\nmarketcap: {data['price_usdt']*(10**9)}$\nhttps://dexscreener.com/solana/{mint}")
    #response = swap("buy", mint, bet, 20, 0.006, data["pool"])
        
def on_message(data):
    print(data)
    side = data.get("txType", None)
    if side is None or side not in ["create"]:
        return
    address = data.get("traderPublicKey", None)
    if data["solAmount"] != 15:
        watching_wallet.pop(address)
        wallet_to_unsubscribe.append(address)
        return
    mint = data["mint"]
    print(f"{side} {mint}")
    send_message(f"{side} {mint}")
    watch_token(mint, data)
    
# Run the subscribe function



response = requests.get('https://api.ipify.org?format=json')
ip_data = response.json()
send_message(ip_data['ip'])

threading.Thread(target=maj_wallet_to_subscribe, daemon=True).start()
asyncio.get_event_loop().run_until_complete(subscribe())
