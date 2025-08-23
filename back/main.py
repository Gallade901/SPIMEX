import requests
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
# DST5CHR001O - мы не закупаем
sids = ['DSC5BTC065J', 'DSC5KIT025A', 'DSC5KIT100U', 'DSC5NVL005A', 'DST5NVL001O', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5ZEL065J', 'DSC5KII065F', 'DSC5NVY065F', 'DSC5NPA100U', 'DSC5OSN065F', 'DSC5SLF100U', 'DSC5YAI065F', 'DSC5CHR100U']
delivery_price_sids = {'DSC5BTC065J': 8464, 'DSC5KIT025A': 1550, 'DSC5KIT100U': 1911, 'DSC5NVL005A': 1225, 'DST5NVL001O': 1225, 'DSC5RNT100U': 3759, 'DSC5LSA100U': 5181, 'DSC5ZEL065J': 7449, 'DSC5KII065F': 3467, 'DSC5NVY065F': 5729, 'DSC5NPA100U': 5100, 'DSC5OSN065F': 8464, 'DSC5SLF100U': 3069, 'DSC5YAI065F': 7094, 'DSC5CHR100U': 5040}
# при автовывозе T = 0 
# в словаре не учитываем трубу, при расчёте T будет отдельный блок для неё
delivery_and_shipment_days = {'DSC5BTC065J': {'delivery': 11, 'shipment': 30}, 'DSC5KIT025A': {'delivery': 0, 'shipment': 0}, 'DSC5NVL005A': {'delivery': 0, 'shipment': 0}, 'DST5NVL001O': {'delivery': 0, 'shipment': 0}, 'DSC5ZEL065J': {'delivery': 10, 'shipment': 27}, 'DSC5KII065F': {'delivery': 4, 'shipment': 20}, 'DSC5NVY065F': {'delivery': 7, 'shipment': 26}, 'DSC5OSN065F': {'delivery': 11, 'shipment': 30}, 'DSC5YAI065F': {'delivery': 14, 'shipment': 33}}
session = requests.Session()
base_url = "https://uat.spx.spimex.com"

app = Flask(__name__)
CORS(app)


def authorize():
    json_string = {"login": "146_596_aig", "password": "Vg7#nLp@xR2tQe9M"}
    response = session.post(f"{base_url}/api/auth", json=json_string)
    if response.status_code == 200:
        data = response.json()
        session.cookies.set("username", data["username"], domain="uat.spx.spimex.com")
        session.cookies.set("sessionId", data["sessionId"], domain="uat.spx.spimex.com")
        session.cookies.set("clientType", "API", domain="uat.spx.spimex.com")
    else:
        print("Authorization error:", response.text)


def get_hist_close():
    json_string = {
        "SIDs" : sids,
        "sort" : "asc",
        "empty" : "skip",
        "period" : "5M"
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


# к hist_vwap добавили цену доставки инструмента и записываем в тот же словарь
def get_hist_close_vwap_with_delivery():
    authorize()
    hist_close_data = get_hist_close()
    for value in hist_close_data:
        sid = value.get("SID")
        hist_vwap = value.get("HIST_VWAP")
        delivery_price = delivery_price_sids.get(sid)
        if hist_vwap is not None:
            vwap_with_delivery = hist_vwap + delivery_price
            value["HIST_VWAP_WITH_DELIVERY"] = vwap_with_delivery
    return hist_close_data


def get_hist_close_prices_with_X():
    authorize()
    hist_close_data = get_hist_close_vwap_with_delivery()
    instruments_delivered_by_oil_pipe = ['DSC5KIT100U', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5NPA100U', 'DSC5SLF100U', 'DSC5CHR100U']
    P = 0.015 / 30  # дневная ставка
    result = []
    for value in hist_close_data:
        sid = value.get("SID")
        hist_vwap = value.get("HIST_VWAP")
        hist_vwap_with_delivery = value.get("HIST_VWAP_WITH_DELIVERY")
        delivery_price = delivery_price_sids.get(sid, 0)
        date = value.get("HIST_CLOSE_DATE")
        day = int(date.split("-")[2])  # число месяца
        if hist_vwap is None:
            continue
        # если инструмент доставляется трубой
        if sid in instruments_delivered_by_oil_pipe:
            delivery = 2  # требуется 2 дня для доставки трубы
            if day <= 16:
                shipment = 14
            else:
                shipment = 35
            T = delivery + shipment
        # жд или автовывоз
        else:
            delivery = delivery_and_shipment_days.get(sid, {}).get("delivery", 0)
            shipment = delivery_and_shipment_days.get(sid, {}).get("shipment", 0)
            T = delivery + shipment
        X = hist_vwap * (1 + P * T) + delivery_price
        result.append({
                "SID": sid,
                "HIST_CLOSE_DATE": date,
                "HIST_VWAP": hist_vwap,
                "HIST_VWAP_WITH_DELIVERY": hist_vwap_with_delivery,
                "X_of_prev_day": X,
                "T": T
            })
    return result


def get_hist_close_prices_with_X_fixed():
    authorize()
    hist_close_data = get_hist_close_vwap_with_delivery()
    P = 0.015 / 30
    instruments_delivered_by_oil_pipe = ['DSC5KIT100U', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5NPA100U', 'DSC5SLF100U', 'DSC5CHR100U']
    data_by_sid = {}
    for v in hist_close_data:
        sid = v["SID"]
        data_by_sid.setdefault(sid, []).append(v) # словарь, у которого ключ-sid и значение-список данных
    for sid in data_by_sid:
        data_by_sid[sid] = sorted(data_by_sid[sid], key=lambda x: x["HIST_CLOSE_DATE"])
    result = []
    for sid, values in data_by_sid.items():
        delivery_price = delivery_price_sids.get(sid, 0)
        for i, current_day in enumerate(values):
            date = current_day.get("HIST_CLOSE_DATE")
            hist_vwap = current_day.get("HIST_VWAP")
            hist_vwap_with_delivery = current_day.get("HIST_VWAP_WITH_DELIVERY")
            if sid in instruments_delivered_by_oil_pipe:
                delivery = 2
                day = int(date.split("-")[2])
                if day <= 16:
                    shipment = 14
                else:
                    shipment = 35
            else:
                delivery = delivery_and_shipment_days.get(sid, {}).get("delivery", 0)
                shipment = delivery_and_shipment_days.get(sid, {}).get("shipment", 0)
            T = delivery + shipment
            if hist_vwap is not None:
                X_of_prev_day = hist_vwap * (1 + P * T) + delivery_price
            # получаем X_10 и X_20 на основе предыдущих 10 и 20 дней
            X_10 = None
            X_20 = None
            if i >= 10:
                # список из значений hist_vwap за последние 10 торговых дней
                prev_10 = [v.get("HIST_VWAP") for v in values[i-10:i] if v.get("HIST_VWAP") is not None]
                if prev_10:
                    X_10 = min(prev_10) * (1 + P * T) + delivery_price
                    #print(f"[{sid}: {date}], prev_10: {prev_10}, min: {min(prev_10)}, T: {T}, delivery_price: {delivery_price}, X_10: {X_10}")
            if i >= 20:
                # список из значений hist_vwap за последние 20 торговых дней
                prev_20 = [v.get("HIST_VWAP") for v in values[i-20:i] if v.get("HIST_VWAP") is not None]
                if prev_20:
                    X_20 = min(prev_20) * (1 + P * T) + delivery_price
                    #print(f"[{sid}: {date}], prev_20: {prev_20}, min: {min(prev_20)}, T: {T}, delivery_price: {delivery_price}, X_20: {X_20}")
            result.append({
                "SID": sid,
                "HIST_CLOSE_DATE": date,
                "HIST_VWAP": hist_vwap,
                "HIST_VWAP_WITH_DELIVERY": hist_vwap_with_delivery,
                "T": T,
                "X_of_prev_day": X_of_prev_day,
                "X_10": X_10,
                "X_20": X_20
            })
    return result



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
    
print(get_trades())


def get_last_price_with_delivery():
    authorize()
    trades_data = get_trades()
    result = []
    for sid, last_price in trades_data.items():
        delivery_price = delivery_price_sids.get(sid, 0)
        if last_price is not None:
            result.append({
                "SID": sid,
                "LAST": last_price,
                "LAST_WITH_DELIVERY": last_price + delivery_price
            })
    return result

print(get_last_price_with_delivery())

# пункт 2.1
def get_monthly_avg_price():
    data = get_hist_close_vwap_with_delivery()
    daily_avg = {}
    for i in data:
        date = i.get("HIST_CLOSE_DATE")
        vwap_with_delivery = i.get("HIST_VWAP_WITH_DELIVERY")
        if vwap_with_delivery == None:
            continue
        if date not in daily_avg:
            daily_avg[date] = [vwap_with_delivery]
        else:
            daily_avg[date].append(vwap_with_delivery)

    # средняя цена дня по всем инструментам
    for date in daily_avg:
        daily_avg[date] = sum(daily_avg[date]) / len(daily_avg[date])
    # Отсортированный по дате массив средних цен
    sorted_by_date_daily_avg = dict(sorted(daily_avg.items()))
    monthly_avg = {}
    for date in sorted_by_date_daily_avg:
        month = date.split("-")[1]
        if month not in monthly_avg:
            monthly_avg[month] = [sorted_by_date_daily_avg[date]]
        else:
            monthly_avg[month].append(sorted_by_date_daily_avg[date])
    
    for month in monthly_avg:
        monthly_avg[month] = sum(monthly_avg[month]) / len(monthly_avg[month])
    
    return daily_avg, monthly_avg


# daily_prices, monthly_price = get_monthly_avg_price()
# print(daily_prices)
# print(monthly_price)


# пункт 2.2
def get_monthly_avg_price_by_tool():
    data = get_hist_close_vwap_with_delivery()
    daily_avg = {}
    for i in data:
        date = i.get("HIST_CLOSE_DATE")
        vwap_with_delivery = i.get("HIST_VWAP_WITH_DELIVERY")
        if vwap_with_delivery == None:
            continue
        if date not in daily_avg:
            daily_avg[date] = [vwap_with_delivery]
        else:
            daily_avg[date].append(vwap_with_delivery)
    
    sorted_by_date_daily_avg = dict(sorted(daily_avg.items()))

    minn_avg = {}
    for date in sorted_by_date_daily_avg:
        minn = min(sorted_by_date_daily_avg[date])
        minn_avg[date] = minn


    monthly_avg = {}
    for date in minn_avg:
        month = date.split("-")[1]
        if month not in monthly_avg:
            monthly_avg[month] = [minn_avg[date]]
        else:
            monthly_avg[month].append(minn_avg[date])
    
    for month in monthly_avg:
        monthly_avg[month] = sum(monthly_avg[month]) / len(monthly_avg[month])

    return minn_avg, monthly_avg


# minn_avg, monthly_price = get_monthly_avg_price_by_tool()
# print(minn_avg)
# print(monthly_price)


# пункт 3
def purchase_for_1_month():
    vol = 1000  # константа - 1000 тонн
    ks = 1
    # hist_close_data = get_hist_close_vwap_with_delivery()
    hist_close_data = get_hist_close_prices_with_X()
    hist_close = {}
    for sid, data in hist_close.items():
        date = data.get("HIST_CLOSE_DATE")
        x_price = data.get("X_of_prev_day")
        if x_price == None:
            continue
        if date not in hist_close:
            hist_close[date] = [x_price]
        else:
            hist_close[date].append(x_price)

    sorted_data_by_date = dict(sorted(hist_close.items()))
    sorted_items = list(sorted_data_by_date.items()) # отсортированный список из кортежей (дата, [цены])

    # имитация закупки раз в неделю (4 раза за месяц)
    # начинаем с 10 дня, т.к нужен sma10
    purchase_volume = 0 # объём закупки за месяц
    counter = 0
    sma10 = 0
    for j in range(10, len(sorted_items), 7):
        if counter >= 4:
            break
        # sma10 для текущего дня
        # j - текущий индекс дня для которого мы производим закупку
        last_10_items = sorted_items[-10:]  # массив данных за 10 дней до текущей покупки
        # print(last_10_items)
        prices_of_last_10_days = []
        for date, items in last_10_items:
            prices_of_last_10_days.extend(items)

        sma10 = sum(prices_of_last_10_days) / len(prices_of_last_10_days)

        prices_of_current_day = sorted_items[j][1]
        x = min(prices_of_current_day)
        print(f"Дата: {sorted_items[j][0]}, X: {x}, SMA10: {sma10}")

        # имитация покупки
        # x ниже sma10 на 2% или более
        if x <= sma10 * 0.98:
            purchase = vol * 0.35 * ks
        # x в пределах +- 1% от sma10
        elif sma10 * 0.99 <= x <= sma10 * 1.01:
            purchase = vol * 0.25 * ks
        # выше на 2%
        elif x > sma10 * 1.02:
            purchase = vol * 0.15 * ks
        # не закупаем
        else:
            purchase = 0
        purchase_volume += purchase
        counter += 1
        print(f"Было закуплено {purchase} тонн за {counter} неделю")
        print(f"SMA10: {sma10}")
    print(f"\nОбщиий объём закупки за месяц: {purchase_volume} тонн")
    return purchase_volume, sma10

a, b = purchase_for_1_month()


def info_for_excel_table():
    hist_data_list = get_hist_close_prices_with_X_fixed()
    hist_data_by_sid = {}
    for item in hist_data_list:
        sid = item["SID"]
        if sid not in hist_data_by_sid:
            hist_data_by_sid[sid] = []
        hist_data_by_sid[sid].append(item)
    result = []
    for sid, hist_days in hist_data_by_sid.items():
        for day in hist_days:
            result.append({
                "SID": sid,
                "Дата": day["HIST_CLOSE_DATE"],
                "HIST_VWAP": day["HIST_VWAP"],
                "HIST_VWAP_WITH_DELIVERY": day["HIST_VWAP_WITH_DELIVERY"],
                "X_10": day["X_10"],
                "X_20": day["X_20"],
                "Vremya_dostavki_s_otgruzkoy": day["T"]
            })
    df = pd.DataFrame(result)
    df.to_excel("hist_close_data.xlsx", index=False)
    return df

info_for_excel_table()


@app.route("/api/table")
def data_table():
    result = []
    trades_data_list = get_last_price_with_delivery()
    trades_data_dict = {i["SID"]: i for i in trades_data_list}

    hist_data_list_with_x_fixed = get_hist_close_prices_with_X_fixed()
    hist_data_dict = {i["SID"]: i for i in hist_data_list_with_x_fixed}

    P = 0.015 / 30  # дневная ставка
    for sid in sids:
        trade = trades_data_dict.get(sid)
        hist_item = hist_data_dict.get(sid)
        if trade is None or hist_item is None:
            continue
        last_price = trade["LAST"]
        last_price_with_delivery = trade["LAST_WITH_DELIVERY"]
        delivery_price = delivery_price_sids.get(sid, 0)
        x = hist_item.get("X_of_prev_day")
        x_10 = hist_item.get("X_10")
        x_20 = hist_item.get("X_20")
        t = hist_item.get("T")
        date = hist_item.get("HIST_CLOSE_DATE")
        last_price_with_rate_and_delivery = None
        if t is not None:
            last_price_with_rate_and_delivery = last_price * (1 + P * t) + delivery_price
        result.append({
            "SID": sid,
            "HIST_CLOSE_DATE": date,
            "X_pred_dnya": x,
            "X_pred_10_dney": x_10,
            "X_pred_20_dney": x_20,
            "Tekuschaya": last_price,
            "Tekuschaya_s_dostavkoy": last_price_with_delivery,
            "Vremya_dostavki_s_otgruzkoy": t,
            "Tekuschaya_s_dostavkoy_P": last_price_with_rate_and_delivery
        })
    sorted_res = sorted(result, key=lambda i: i.get("Tekuschaya_s_dostavkoy_P"))
    return jsonify(sorted_res)
      

@app.route("/api/purchase_volume")
def purchase_volume():
    volume, sma10 = purchase_for_1_month()
    return jsonify({"purchase_volume": volume, "sma10": sma10})

@app.route("/api/monthly_avg_price")
def monthly_avg_price():
    daily_prices, monthly_price = get_monthly_avg_price()
    return jsonify({"daily_prices": daily_prices, "monthly_price": monthly_price})

@app.route("/api/monthly_avg_price_by_tool")
def monthly_avg_price_by_tool():
    minn_avg, monthly_price = get_monthly_avg_price_by_tool()
    return jsonify({"minn_avg": minn_avg, "monthly_price": monthly_price})

if __name__ == "__main__":
    app.run(debug=True)




