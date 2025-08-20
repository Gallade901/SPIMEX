import requests
# DST5CHR001O - мы не закупаем
sids = ['DSC5BTC065J', 'DSC5KIT025A', 'DSC5KIT100U', 'DSC5NVL005A', 'DST5NVL001O', 'DSC5RNT100U', 'DSC5LSA100U', 'DSC5ZEL065J', 'DSC5KII065F', 'DSC5NVY065F', 'DSC5NPA100U', 'DSC5OSN065F', 'DSC5SLF100U', 'DSC5YAI065F', 'DSC5CHR100U']
delivery_price_sids = {'DSC5BTC065J': 8464, 'DSC5KIT025A': 1550, 'DSC5KIT100U': 1911, 'DSC5NVL005A': 1225, 'DST5NVL001O': 1225, 'DSC5RNT100U': 3759, 'DSC5LSA100U': 5181, 'DSC5ZEL065J': 7449, 'DSC5KII065F': 3467, 'DSC5NVY065F': 5729, 'DSC5NPA100U': 5100, 'DSC5OSN065F': 8464, 'DSC5SLF100U': 3069, 'DSC5YAI065F': 7094, 'DSC5CHR100U': 5040}
session = requests.Session()
base_url = "https://uat.spx.spimex.com"


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



def get_trades():
    json_string = {
        "SIDs" : sids,
        "sort" : "asc",
        "empty" : "skip",
        "period" : "5M"
    }
    feed = "SPIMEX_STE"
    trades_rows = []
    response = session.post(f"{base_url}/api/history/{feed}", json=json_string)
    if response.status_code == 200:
        data = response.json()
        all_history = data.get("response", [])
        for i in all_history:
            sid = i.get("SID")
            fields = i.get("fields", {})
            trades_data = fields.get("trades", [])
            for trade in trades:
                trade["SID"] = sid
                trades_rows.append(trade)
    return trades_rows


# пункт 3
def purchase_for_1_month():
    vol = 1000  # константа - 1000 тонн
    ks = 1
    hist_close = {}
    hist_close_data = get_hist_close_vwap_with_delivery()
    for i in hist_close_data:
        date = i.get("HIST_CLOSE_DATE")
        vwap_with_delivery = i.get("HIST_VWAP_WITH_DELIVERY")
        if vwap_with_delivery == None:
            continue
        if date not in hist_close:
            hist_close[date] = [vwap_with_delivery]
        else:
            hist_close[date].append(vwap_with_delivery)

    sorted_data_by_date = dict(sorted(hist_close.items()))
    sorted_items = list(sorted_data_by_date.items()) # отсортированный список из кортежей (дата, [цены])
    
    # имитация закупки раз в неделю (4 раза за месяц)
    # начинаем с 10 дня, т.к нужен sma10
    purchase_volume = 0 # объём закупки за месяц
    counter = 0
    buy_for_month = 4
    SMA10 = 10
    # 20 августа
    # len = 100
    for j in range(10, len(sorted_items), 7):
        if counter >= buy_for_month:
            break
        # sma10 для текущего дня
        # j - текущий индекс дня для которого мы производим закупку
        last_10_items = sorted_items[-SMA10:]  # массив данных за 10 дней до текущей покупки
        #print(last_10_items)
        prices_of_last_10_days = []

        for date, items in last_10_items:
            prices_of_last_10_days.extend(items)
        sma10 = sum(prices_of_last_10_days) / len(prices_of_last_10_days)

        prices_of_current_day = sorted_items[j][1] # Самая последняя завершенная сделка её цена
        x = min(prices_of_current_day) #

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
    return purchase_volume

purchase_for_1_month()







