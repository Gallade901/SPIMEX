from datetime import datetime, timedelta
import pandas as pd

from main import get_hist_close_prices_with_X_fixed



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
    for day in hist_date:
        sorted_by_price_X =  sorted(hist_date[day], key=lambda x: x['X'])
        d = 0
        for i in range(len(sorted_by_price_X)):
            sorted_by_price_X[i]["rating"] = 15 - d
            d += 1        
            if sorted_by_price_X[i]["SID"] in sid_count_summ:
                sid_count_summ[sorted_by_price_X[i]["SID"]]["count"] += 1
                sid_count_summ[sorted_by_price_X[i]["SID"]]["summ"] += sorted_by_price_X[i]["rating"]
            else:
                sid_count_summ[sorted_by_price_X[i]["SID"]] = {"count": 1, "summ": sorted_by_price_X[i]["rating"]}
            new_date = sorted_by_price_X[i]["HIST_CLOSE_DATE"].split("-")[1]
            date_obj = datetime.strptime(sorted_by_price_X[i]["HIST_CLOSE_DATE"], "%Y-%m-%d")
            new_date = date_obj + timedelta(days=sorted_by_price_X[i]["T"])
            new_date_old_format = new_date.strftime("%Y-%m-%d")
            sorted_by_price_X[i]["data_30"] = new_date_old_format
        result.extend(sorted_by_price_X)
    
    
    # sid_count_summ = [{"s":1}]
    df1 = pd.DataFrame(result)
    df2 = pd.DataFrame(sid_count_summ)
    with pd.ExcelWriter('hist_close_data.xlsx') as writer:
        df1.to_excel(writer, sheet_name='top', index=False)
        df2.to_excel(writer, sheet_name='final', index=False)


info_for_excel_table()