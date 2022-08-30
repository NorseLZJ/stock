"""
日线级别金叉,周期[5~10]天以内的
"""
from comm import *
import akshare as ak
import numpy as np


def jc_ten_five_day(x):
    df = get_10_daily_data(x["股票代码"])
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)
    if len(df) < 10:
        return np.nan

    for i in (-1, -11, -1):
        dif = df.iloc[i]["dif"]
        dea = df.iloc[i]["dea"]
        # 前面没有金叉
        if i == -1 and dif <= dea:
            return np.nan

        # 金叉超过5天
        if i <= -5 and dif < dea:
            print("find %s" % (x["股票代码"]))
            return 1

    return np.nan


if __name__ == "__main__":
    # jc_ten_five_day({"股票代码": "002424"})

    df = ak.stock_lrb_em()
    df = clean_data_by_name(df, "lrb")
    df.dropna(inplace=True)
    df["buy"] = df.apply(lambda x: jc_ten_five_day(x), axis=1)
    df["industry"] = df.apply(
        lambda x: get_industry(x["股票代码"], x["股票简称"]), axis=1
    )
    df.dropna(inplace=True)
    df.drop(columns=["buy"], axis=1, inplace=True)
    df.sort_values(
        by=["industry"],
        inplace=True,
        ignore_index=True,
        ascending=False,
    )

    df.to_excel("out/5~10天金叉.xlsx", index=False)
