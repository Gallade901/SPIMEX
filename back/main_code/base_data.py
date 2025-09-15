import requests

# DST5CHR001O - мы не закупаем
sids = ['DSC5BTC065J', 'DSC5KIT025A', 'DSC5KIT100U', 'DSC5NVL005A', 'DST5NVL001O', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5ZEL065J', 'DSC5KII065F', 'DSC5NVY065F', 'DSC5NPA100U', 'DSC5OSN065F', 'DSC5SLF100U', 'DSC5YAI065F', 'DSC5CHR100U']
delivery_price_sids = {'DSC5BTC065J': 8464, 'DSC5KIT025A': 1550, 'DSC5KIT100U': 1911, 'DSC5NVL005A': 1225, 'DST5NVL001O': 1225, 'DSC5RNT100U': 3759, 'DSC5LSA100U': 5181, 'DSC5ZEL065J': 7449, 'DSC5KII065F': 3467, 'DSC5NVY065F': 5729, 'DSC5NPA100U': 5100, 'DSC5OSN065F': 8464, 'DSC5SLF100U': 3069, 'DSC5YAI065F': 7094, 'DSC5CHR100U': 5040}
session = requests.Session()
base_url = "https://spx.spimex.com" #uat.spx.spimex.com - тестовый

def authorize():
    json_string = {"login": "157_614_aip", "password": "bp39ciRT@H"}
    response = session.post(f"{base_url}/api/auth", json=json_string)
    if response.status_code == 200:
        data = response.json()
        session.cookies.set("username", data["username"], domain="uat.spx.spimex.com")
        session.cookies.set("sessionId", data["sessionId"], domain="uat.spx.spimex.com")
        session.cookies.set("clientType", "API", domain="spx.spimex.com")#spx.spimex.com  uat.spx.spimex.com
    else:
        print("Authorization error:", response.text)


def get_hist_close():
    json_string = {
        "SIDs" : sids,
        "sort" : "asc",
        "empty" : "skip",
        "period" : "10Y"
    }
    feed = "SPIMEX_STE"
    hist_close_rows = []
    response = session.post(f"{base_url}/api/history/{feed}", json=json_string)
    if response.status_code == 200:
        data = response.json()
        all_history = data.get("response", [])
        for i in all_history:
            sid = i.get("SID")
            fields = i.get("fields", {})
            hist_close = fields.get("hist_close", [])
            for hist in hist_close:
                hist["SID"] = sid
                hist_close_rows.append(hist)
    return hist_close_rows

def get_trades():
    authorize()
    json_string = {
        "SIDs": sids,
        "sort": "desc",
        "empty": "skip",
        "period": "1M"
    }
    feed = "SPIMEX_STE"
    prices = {}
    response = session.post(f"{base_url}/api/history/{feed}", json=json_string)
    if response.status_code == 200:
        data = response.json()
        all_history = data.get("response", [])
        for i in all_history:
            sid = i.get("SID")
            fields = i.get("fields", {})
            trades = fields.get("trades", [])
            if trades:
                last_trade = trades[0]
                last_price = last_trade.get("LAST")
                if last_price is not None:
                    prices[sid] = last_price
    return prices