from flask import Flask, jsonify
from flask_cors import CORS

from base_data import authorize, get_hist_close, get_trades

# DST5CHR001O - мы не закупаем
sids = ['DSC5BTC065J', 'DSC5KIT025A', 'DSC5KIT100U', 'DSC5NVL005A', 'DST5NVL001O', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5ZEL065J', 'DSC5KII065F', 'DSC5NVY065F', 'DSC5NPA100U', 'DSC5OSN065F', 'DSC5SLF100U', 'DSC5YAI065F', 'DSC5CHR100U']
delivery_price_sids = {'DSC5BTC065J': 8464, 'DSC5KIT025A': 1550, 'DSC5KIT100U': 1911, 'DSC5NVL005A': 1225, 'DST5NVL001O': 1225, 'DSC5RNT100U': 3759, 'DSC5LSA100U': 5181, 'DSC5ZEL065J': 7449, 'DSC5KII065F': 3467, 'DSC5NVY065F': 5729, 'DSC5NPA100U': 5100, 'DSC5OSN065F': 8464, 'DSC5SLF100U': 3069, 'DSC5YAI065F': 7094, 'DSC5CHR100U': 5040}
# при автовывозе T = 0 
# в словаре не учитываем трубу, при расчёте T будет отдельный блок для неё
delivery_and_shipment_days = {'DSC5BTC065J': {'delivery': 11, 'shipment': 30}, 'DSC5KIT025A': {'delivery': 0, 'shipment': 0}, 'DSC5NVL005A': {'delivery': 0, 'shipment': 0}, 'DST5NVL001O': {'delivery': 0, 'shipment': 0}, 'DSC5ZEL065J': {'delivery': 10, 'shipment': 27}, 'DSC5KII065F': {'delivery': 4, 'shipment': 20}, 'DSC5NVY065F': {'delivery': 7, 'shipment': 26}, 'DSC5OSN065F': {'delivery': 11, 'shipment': 30}, 'DSC5YAI065F': {'delivery': 14, 'shipment': 33}}

app = Flask(__name__)
CORS(app)

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
                "X": X,
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
                X = hist_vwap * (1 + P * T) + delivery_price
            else:
                continue
            # получаем X_10 и X_20 на основе предыдущих 10 и 20 дней
            X_10 = None
            X_20 = None
            if i >= 10:
                # список из значений hist_vwap за последние 10 торговых дней
                prev_10 = [v.get("HIST_VWAP") for v in values[i-10:i] if v.get("HIST_VWAP") is not None]
                if prev_10:
                    X_10 = sum(prev_10) / (len(prev_10)) * (1 + P * T) + delivery_price
            if i >= 20:
                # список из значений hist_vwap за последние 20 торговых дней
                prev_20 = [v.get("HIST_VWAP") for v in values[i-20:i] if v.get("HIST_VWAP") is not None]
                if prev_20:
                    X_20 = sum(prev_20) / (len(prev_20)) * (1 + P * T) + delivery_price
            result.append({
                "SID": sid,
                "HIST_CLOSE_DATE": date,
                "HIST_VWAP": hist_vwap,
                "HIST_VWAP_WITH_DELIVERY": hist_vwap_with_delivery,
                "T": T,
                "X": X,
                "X_10": X_10,
                "X_20": X_20
            })
    return result
    

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
        x = hist_item.get("X")
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
      

if __name__ == "__main__":
    app.run(host='0.0.0.0')




