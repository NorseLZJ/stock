"""
日线级别金叉,周期[5~10]天以内的
"""
from comm import *
import akshare as ak
import numpy as np
from lrb import *
from industry import *
from datetime import datetime, date
import datetime as dt


def jc_5_10_day(symbol: str):
    td = dt.date.today()
    de = str(td).replace("-", "")
    ds, _ = get_before_day(30)

    df = get_daily_data(symbol, start_date=ds, end_date=de)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)
    if len(df) < 10:
        return np.nan

    for i in (-1, -11, -1):
        dif, dea = g_vbs(df.iloc[i], ["dif", "dea"])
        # 前面没有金叉
        if i == -1 and dif <= dea:
            return np.nan

        # 金叉超过5天
        if i <= -5 and dif < dea:
            print("find %s" % (symbol))
            return 1

    return np.nan


if __name__ == "__main__":
    # jc_ten_five_day({"股票代码": "002424"})

    df = ak.stock_lrb_em()
    df = CleanLRB(df)
    df.dropna(inplace=True)
    industry = Industry()
    df["buy"] = df.apply(lambda x: jc_5_10_day(x["股票代码"]), axis=1)
    df["industry"] = df.apply(lambda x: industry.GetIndustry(x["股票代码"]), axis=1)
    df.dropna(inplace=True)
    df.drop(columns=["buy"], axis=1, inplace=True)
    DelLRBColumn(df)
    df.sort_values(
        by=["industry"],
        inplace=True,
        ignore_index=True,
        ascending=False,
    )
    df.to_excel("out/5~10天金叉.xlsx", index=False)
