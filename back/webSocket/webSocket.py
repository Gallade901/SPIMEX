import requests
import websocket # pip install websocket-client
# from flask import Flask, jsonify
# from flask_cors import CORS
import json

session = requests.Session()
sids = ['DSC5BTC065J', 'DSC5KIT025A', 'DSC5KIT100U', 'DSC5NVL005A', 'DST5NVL001O', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5ZEL065J', 'DSC5KII065F', 'DSC5NVY065F', 'DSC5NPA100U', 'DSC5OSN065F', 'DSC5SLF100U', 'DSC5YAI065F', 'DSC5CHR100U']
base_url = "https://uat.spx.spimex.com"
feed = "SPIMEX_STE"
websocket_url = "wss://uat.spx.spimex.com/ws"
ws = None

# app = Flask(__name__)
# CORS(app)


def authorize():
    json_string = {"login": "146_596_aig", "password": "Vg7#nLp@xR2tQe9M"}
    response = session.post(f"{base_url}/api/auth", json=json_string)
    if response.status_code == 200:
        data = response.json()
        # session.cookies.set("username", data["username"], domain="uat.spx.spimex.com")
        # session.cookies.set("sessionId", data["sessionId"], domain="uat.spx.spimex.com")
        # session.cookies.set("clientType", "API", domain="uat.spx.spimex.com")
        print("Authorization successful!")
        print("Response Headers:", response.headers)
    else:
        print("Authorization error:", response.text)

def on_message(ws, message):
    print("Received:", message)
    if message == "\n":
        ws.send("\n")
        print("Heart-beat responded.")
    else:
        try:
            data = json.loads(message)
            # Check if the message is for the desired feed and SIDs
            if isinstance(data, dict) and data.get("feed") == feed and data.get("SID") in sids:
                print(f"Relevant data for {data['feed']} and {data['SID']}: {data}")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("feed") == feed and item.get("SID") in sids:
                        print(f"Relevant data for {item['feed']} and {item['SID']}: {item}")
            else:
                print("Non-heartbeat message:", message)
        except json.JSONDecodeError:
            print("Non-JSON message:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"Closed with status: {close_status_code}, message: {close_msg}")

def on_open(ws):
    print("Opened connection")
    cookie_str = ""
    wsid = ""
    for cookie in session.cookies:
        cookie_str += f"{cookie.name}={cookie.value}; "
        if cookie.name == "sessionId":
            wsid = cookie.value
    cookie_str = cookie_str.strip()
    

    # headers = {
    #     "accept-version": "1.2",
    #     "heart-beat": "0,10000", # N = 10000ms (10 seconds)
    #     "Cookie": cookie_str
    # }
    ws.send("CONNECT\n" +
            "accept-version:1.2\n" +
            "heart-beat:0,10000\n" +
            f"Cookie:{cookie_str}\n\n\x00")

    print(f"CONNECT frame sent with Cookie: {cookie_str}")

    # Example usage: subscribe to a topic after connection is open
    subscribe(ws, wsid)
    # Example usage: subscribe to instruments
    send_subscribe_instruments(ws, feed, sids)


def subscribe(ws, own_id):
    ws.send(f"SUBSCRIBE\n" +
            f"destination:/user/queue/reply\n" +
            f"id:{own_id}\n\n\x00")
    print(f"Subscribed with ID: {own_id}")

def unsubscribe(ws, own_id):
    ws.send(f"UNSUBSCRIBE\n" +
            f"id:{own_id}\n\n\x00")
    print(f"Unsubscribed with ID: {own_id}")

def send_subscribe_instruments(ws, feed, sids):
    body = json.dumps({"feed": feed, "SIDs": sids})
    ws.send(f"SEND\n" +
            f"destination:/app/message\n" +
            f"content-type:application/json\n" +
            f"content-length:{len(body)}\n\n" +
            f"{body}\x00")
    print(f"Sent subscribe instruments for feed: {feed}, SIDs: {sids}")

def send_unsubscribe_instruments(ws, feed, sids):
    body = json.dumps({"feed": feed, "SIDs": sids})
    ws.send(f"SEND\n" +
            f"destination:/app/message/unsubscribe\n" +
            f"content-type:application/json\n" +
            f"content-length:{len(body)}\n\n" +
            f"{body}\x00")
    print(f"Sent unsubscribe instruments for feed: {feed}, SIDs: {sids}")

def connect_websocket():
    global ws
    authorize()

    cookie_str = ""
    for cookie in session.cookies:
        cookie_str += f"{cookie.name}={cookie.value}; "
    cookie_str = cookie_str.strip()

    headers = {
        "Cookie": cookie_str
    }

    ws = websocket.WebSocketApp(websocket_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=headers)
    # To ensure we can access these functions globally or pass them around
    # you might want to consider making them part of a class structure
    # or passing them as arguments if you want to make the code more modular.
    # For simplicity, and based on the current structure, they are global for now.
    ws.run_forever()

if __name__ == "__main__":
    connect_websocket()
