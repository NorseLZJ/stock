"""
近90个交易日上升趋势
"""

import pandas as pd
from comm import *
import time
from industry import *

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

time_prefix = time.strftime("%Y_%m_%d", time.localtime(time.time()))


def calc(code: str):
    if invide_stock_code(code) is False:
        return np.nan

    df = get_daily_data(code)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)
    if len(df) <= 90:
        return np.nan

    last_v = df.iloc[-1]
    last_ma60, last_date = last_v["ma60"], last_v["date"]
    prev_v = df.iloc[-90]
    prev_ma60, prev_date = prev_v["ma60"], prev_v["date"]

    # 好长时间没有k线的，跳过
    # if time_prefix != last_date:
    #    return np.nan

    if last_ma60 < prev_ma60:
        return np.nan

    subma60 = (float(last_ma60 - prev_ma60) / float(prev_ma60)) * 100
    if subma60 > 15:
        return np.nan

    idx = -1
    while idx >= -90:
        # 最近90个交易日有某天股价在60日线上方10%的位置
        v = df.iloc[idx]
        ma60, close = v["ma60"], v["close"]
        if close > ma60:
            ret = (float(close - ma60) / float(ma60)) * 100
            if ret > 10:
                return np.nan
        idx -= 1

    print("手工校验下:%s" % code)
    return format("%s~%s  %.3f,%.3f" % (prev_date, last_date, prev_ma60, last_ma60))


if __name__ == "__main__":
    create_dir(["data", "out"])
    df = ak.stock_lrb_em()
    df = df.loc[
        (df["净利润同比"] > 5.0)
        & (df["净利润同比"] < 300.0)
        & (df["股票简称"].str.find("ST") == -1)
        & (df["股票简称"].str.find("退") == -1),
        :,
    ]
    df.to_csv("temp.csv", index=False)
    industry = Industry()
    df["industry"] = df.apply(lambda x: industry.GetIndustry(x["股票代码"]), axis=1)
    df["signle"] = df.apply(lambda x: calc(x["股票代码"]), axis=1)
    df.sort_values(
        by=["industry", "净利润同比"],
        inplace=True,
        ignore_index=True,
        ascending=False,
    )

    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)

    out_file = format("out/90日上升趋势_%s.csv" % (time_prefix))
    df.drop(
        inplace=True,
        columns=[
            "净利润",
            "净利润同比",
            "营业总收入",
            "营业总收入同比",
            "营业总支出-营业支出",
            "营业总支出-销售费用",
            "营业总支出-管理费用",
            "营业总支出-财务费用",
            "营业总支出-营业总支出",
            "营业利润",
            "利润总额",
            # "公告日期",
            "industry",
            "signle",
            "序号",
        ],
    )
    df.to_csv(out_file, index=False)
    if os.path.exists("temp.csv"):
        os.remove("temp.csv")
