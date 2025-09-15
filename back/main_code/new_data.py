from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
session = requests.Session()

# получение курса доллара к рублю
def get_usd_rub_rate(start_date="2024-09-14", end_date="2025-09-14"):
    d1 = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    d2 = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={d1}&date_req2={d2}&VAL_NM_RQ=R01235"
    response = requests.get(url)
    rates = []
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for record in root.findall("Record"):
            date_str = record.attrib["Date"]
            date_iso = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            value_str = record.find("Value").text.replace(",", ".")
            rate = float(value_str)
            rates.append([date_iso, rate])
    return rates
print(get_usd_rub_rate())

# котировки из Роттердама - MGO, VLSFO, LSMGO
def get_bunker_prices(oil_types):
    base_url = "https://shipandbunker.com/a/.json"
    try:
        payload = {
            "api-method": "pricesForAllSeriesGet",
            "resource": "MarketPriceGraph_Block",
            "mc0": "NL RTM"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://shipandbunker.com/",
            "X-Requested-With": "XMLHttpRequest"
        }
        response = session.post(base_url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = {}
        days_data = data["api"]["NL RTM"]["data"]["day_list"]
        prices_data = data["api"]["NL RTM"]["data"]["prices"]
        for oil_type in oil_types:
            timestamps = days_data.get(oil_type)
            day_prices = prices_data.get(oil_type, {}).get("dayprice")
            if timestamps and day_prices:
                parsed_list = []
                for day_id, price in day_prices:
                    timestamps_ms = timestamps.get(str(day_id))
                    if timestamps_ms:
                        date = datetime.fromtimestamp(timestamps_ms/1000)
                        formatted_date = date.strftime("%Y-%m-%d")
                        parsed_list.append({
                            "date": formatted_date,
                            "price": price
                        })
                result[oil_type] = parsed_list
    except Exception as e:
        print(e)
        return None
    return result

oil_types = ['MGO', 'VLSFO', 'LSMGO']
print(get_bunker_prices(oil_types))


# показатели для вычета акциза за несколько лет
def get_data_from_table():
    months = [ "январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
    base_url = "https://fas.gov.ru/pages/pokazateli-dla-vycheta-akciza"
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = []
    for tr in table.find("tbody").find_all("tr", recursive=False):
        row = [td.get_text(strip=True).replace("\xa0", "") for td in tr.find_all("td")]
        if any(row):
            rows.append(row)
    results = {}
    current_indicator = None
    # первая строка — заголовки с месяцами
    for row in rows[1:]:
        indicator_name = row[0]
        values = row[1:]
        # если строка это заголовок (все значения пустые)
        if all(v == "" for v in values):
            current_indicator = indicator_name or None
            if current_indicator:
                results[current_indicator] = {}
            continue
        # если нет показателя, то пропускаем
        if not current_indicator:
            continue
        # обычная строка с данными
        results[current_indicator][indicator_name] = {
            month: (val if val else None) for month, val in zip(months, values)
        }
    return results
print(get_data_from_table())

def calculate_sma(period, hist_close_data):
    hist_close = {}
    for data in hist_close_data:
        date = data.get("HIST_CLOSE_DATE")
        x_price = data.get("X_1")
        if x_price is None:
            continue
        if date not in hist_close:
            hist_close[date] = [x_price]
        else:
            hist_close[date].append(x_price)
    sorted_data_by_date = dict(sorted(hist_close.items()))
    sorted_items = list(sorted_data_by_date.items())  # отсортированный список из кортежей (дата, [цены])
    last_days = sorted_items[-period:] # последние period дней
    prices = []
    for date, price in last_days:
        prices.extend(price)
    sma = sum(prices) / len(prices)
    return sma

test_data = [
    {"HIST_CLOSE_DATE": "2025-09-01", "X_1": 100},
    {"HIST_CLOSE_DATE": "2025-09-02", "X_1": 102},
    {"HIST_CLOSE_DATE": "2025-09-03", "X_1": 101},
    {"HIST_CLOSE_DATE": "2025-09-04", "X_1": 103},
    {"HIST_CLOSE_DATE": "2025-09-05", "X_1": 104},
    {"HIST_CLOSE_DATE": "2025-09-06", "X_1": 105},
]

#sma_4 = calculate_sma(4, test_data)
#sma_10 = calcular_sma(10, get_hist_close_prices_with_X_fixed())











