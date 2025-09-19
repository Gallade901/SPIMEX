from datetime import datetime, timedelta
import pandas as pd

from main import get_hist_close_prices_with_X_fixed
from base_data import get_hist_close, all_data

def info_for_excel_table():
    hist_data_list = get_hist_close_prices_with_X_fixed()
    result = []
    hist_date = {}
    for day in hist_data_list:
        if day["HIST_CLOSE_DATE"] in hist_date:
            hist_date[day["HIST_CLOSE_DATE"]].append(day)
        else:
            hist_date[day["HIST_CLOSE_DATE"]] = [day]
    sid_count_summ = {}
    for day in sorted(hist_date.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d")):
        d = 0
        for i in hist_date[day]:
            i["rating"] = 15 - d
            d += 1
            sid = i["SID"]
            if sid in sid_count_summ:
                sid_count_summ[sid]["count"] += 1
                sid_count_summ[sid]["summ"] += i["rating"]
            else:
                sid_count_summ[sid] = {"count": 1, "summ": i["rating"]}
            date_obj = datetime.strptime(i["HIST_CLOSE_DATE"], "%Y-%m-%d")
            new_date = date_obj + timedelta(days=i["T"])
            i["data_30"] = new_date.strftime("%Y-%m-%d")
        result.extend(hist_date[day])

    # sid_count_summ = [{"s":1}]
    df1 = pd.DataFrame(result)
    df2 = pd.DataFrame(sid_count_summ)
    with pd.ExcelWriter('hist_close_data.xlsx') as writer:
        df1.to_excel(writer, sheet_name='top', index=False)
        df2.to_excel(writer, sheet_name='final', index=False)


# info_for_excel_table()

def process_and_export_to_excel(data):
    res = data.get("response")
    instrument_data = []
    trades_data = []
    hist_close_data = []
    orders_data = []
    for i in res:
        sid = i.get("SID")
        fields = i.get("fields", {})
        hist_close = fields.get("hist_close", [])
        instrument_data.extend(fields.get("instrument"))
        orders_data.extend(fields.get("orders"))
        trades = fields.get("trades")
        for t in trades:
            t["SID"] = sid
            trades_data.append(t)
        for hist in hist_close:
            hist["SID"] = sid
            hist_close_data.append(hist)

    # Convert instrument data to a DataFrame
    # For instrument, it's a single row of data, so we put it in a list
    instrument_df = pd.DataFrame(instrument_data)

    # Convert trades data to a DataFrame
    trades_df = pd.DataFrame(trades_data)

    # Convert orders data to a DataFrame
    orders_df = pd.DataFrame(orders_data)

    # Convert hist_close data to a DataFrame
    hist_close_df = pd.DataFrame(hist_close_data)

    # Define the Excel file name
    excel_file_name = "SPIMEX_Data.xlsx"

    with pd.ExcelWriter(excel_file_name, engine='xlsxwriter') as writer:
        # Write instrument data to a sheet named 'Instrument'
        instrument_df.to_excel(writer, sheet_name='Instrument', index=False)
        print(f"Instrument data written to sheet 'Instrument' in {excel_file_name}")

        # Write trades data to a sheet named 'Trades'
        trades_df.to_excel(writer, sheet_name='Trades', index=False)
        print(f"Trades data written to sheet 'Trades' in {excel_file_name}")

        # Write orders data to a sheet named 'Orders'
        orders_df.to_excel(writer, sheet_name='Orders', index=False)
        print(f"Orders data written to sheet 'Orders' in {excel_file_name}")

        # Write hist_close data to a sheet named 'Hist_Close'
        hist_close_df.to_excel(writer, sheet_name='Hist_Close', index=False)
        print(f"Historical Close data written to sheet 'Hist_Close' in {excel_file_name}")

data = all_data()
process_and_export_to_excel(data)