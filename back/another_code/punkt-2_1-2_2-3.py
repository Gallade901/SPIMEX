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


# пункт 3
def purchase_for_1_month():
    vol = 1000  # константа - 1000 тонн
    ks = 1
    # hist_close_data = get_hist_close_vwap_with_delivery()
    hist_close_data = get_hist_close_prices_with_X()
    hist_close = {}
    for sid, data in hist_close.items():
        date = data.get("HIST_CLOSE_DATE")
        x_price = data.get("X")
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


# @app.route("/api/purchase_volume")
# def purchase_volume():
#     volume, sma10 = purchase_for_1_month()
#     return jsonify({"purchase_volume": volume, "sma10": sma10})

# @app.route("/api/monthly_avg_price")
# def monthly_avg_price():
#     daily_prices, monthly_price = get_monthly_avg_price()
#     return jsonify({"daily_prices": daily_prices, "monthly_price": monthly_price})

# @app.route("/api/monthly_avg_price_by_tool")
# def monthly_avg_price_by_tool():
#     minn_avg, monthly_price = get_monthly_avg_price_by_tool()
#     return jsonify({"minn_avg": minn_avg, "monthly_price": monthly_price})
