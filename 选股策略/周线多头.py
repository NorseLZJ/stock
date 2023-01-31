"""
周线级别多头排列
"""
from comm import *
import akshare as ak
import numpy as np
from lrb import *
from industry import *
from datetime import datetime, date
import datetime as dt


def is_up_weekly(symbol: str):
    """
    td = dt.date.today()
    de = str(td).replace("-", "")
    ds, _ = get_before_day(30)
    """

    df = get_weekly_data(symbol)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)
    if len(df) < 10:
        return np.nan

    ma5, ma10, ma20 = g_vbs(df.iloc[-1], ["ma5", "ma10", "ma20"])
    if ma5 >= ma10 >= ma20:
        print("find %s" % (symbol))
        return 1

    return np.nan


if __name__ == "__main__":
    df = ak.stock_lrb_em()
    df = CleanLRB(df)
    df.dropna(inplace=True)
    industry = Industry()
    df["buy"] = df.apply(lambda x: is_up_weekly(x["股票代码"]), axis=1)
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
    df.to_excel("out/周线级别多头.xlsx", index=False)
