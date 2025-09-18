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


info_for_excel_table()