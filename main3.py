from tools import *
import asyncio
import websockets
import json
import threading
from datetime import datetime

async def subscribe():
    uri = "wss://pumpportal.fun/api/data"
    async with websockets.connect(uri) as websocket:
        print("WebSocket connection established.")

        async def handle_subscriptions():
            while True:
                # Gestion des abonnements
                if wallet_to_subscribe:
                    payload = {
                        "method": "subscribeAccountTrade",
                        "keys": wallet_to_subscribe
                    }
                    await websocket.send(json.dumps(payload))
                    print(f"Subscribed to: {wallet_to_subscribe}")
                    wallet_to_subscribe.clear()

                # Gestion des désabonnements
                if wallet_to_unsubscribe:
                    payload = {
                        "method": "unsubscribeAccountTrade",
                        "keys": wallet_to_unsubscribe
                    }
                    await websocket.send(json.dumps(payload))
                    print(f"Unsubscribed from: {wallet_to_unsubscribe}")
                    wallet_to_unsubscribe.clear()

                # Petite pause pour éviter un CPU 100% (mais sans sleep perceptible pour l'utilisateur)
                await asyncio.sleep(10)

        async def handle_messages():
            async for message in websocket:
                print(f'{datetime.now().strftime("%H:%M:%S")}:{round((time.time()-int(time.time()))*100)}')
                data = json.loads(message)
                on_message(data)

        # Exécuter les deux tâches simultanément
        await asyncio.gather(handle_subscriptions(), handle_messages())

def on_message(data):
    print(data)
    side = data.get("txType", None)
    if side is None or side not in ["buy", "sell"]:
        return
    address = data.get("traderPublicKey", None)
    if data["solAmount"] != 15:
        watching_wallet.pop(address)
        wallet_to_unsubscribe.append(address)
        return
    mint = data["mint"]
    print(f"{side} {mint}")
    if side == "buy":
        #response = swap("buy", mint, bet, 20, 0.006, data["pool"])
        send_message(f"{side} {mint}")
        
# Run the subscribe function
send_message('lancement')
threading.Thread(target=maj_wallet_to_subscribe).start()
asyncio.get_event_loop().run_until_complete(subscribe())