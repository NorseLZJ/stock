"""
获取数据
    利润

默认按照最新的日期获取

*****************************

文档地址:
    https://www.akshare.xyz/tutorial.html

净利润同比为正,
近1年下跌超过50%

"""

from tracemalloc import start
import akshare as ak
import pandas as pd
import os
from comm import *
import time

time_prefix = time.strftime("%Y_%m_%d", time.localtime(time.time()))

pd.set_option("display.max_rows", 1000)
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
# 设置命令行输出时的列对齐功能
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


def check_ma60(df: pd.DataFrame):
    if len(df) < 20:
        return False
    last_ma60 = 0
    last_price = 0.0
    prev_ma60 = 0
    size = len(df) - 1
    count = 0
    while size >= 0:
        v = df.iloc[size]
        close, cma60 = v["close"], v["ma60"]
        if last_ma60 == 0:
            last_ma60 = cma60
            last_price = close
        count += 1
        size -= 1
        if count >= 20:
            prev_ma60 = cma60
            break
    if last_ma60 > prev_ma60:
        subval = float(last_price - last_ma60)
        rate = (subval / float(last_ma60)) * 100
        if rate <= 5.0:
            return True
    return False


def calc(symbol: str, code: str):
    prefix = code[0:3]
    if prefix not in ("000", "300", "600"):
        return np.nan

    df = get_daily_data(code)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True)
    if len(df) <= 0:
        return np.nan

    # print(df.head(5))
    # print(df.tail(5))

    max_idx = len(df) - 1
    if max_idx < 150:  # 股票日销不到120个，太少
        return np.nan

    count = 0
    found = False
    while max_idx >= 0:
        t_val = df.iloc[max_idx]["close"]
        t_ma60 = df.iloc[max_idx]["ma60"]
        if t_val < t_ma60:
            count += 1
        elif count >= 150:
            found = True
            break
        else:
            count = 0
        max_idx -= 1

    if found:
        print("手工校验下:%s" % code)
        return 1
    else:
        return np.nan


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")

    df2 = ak.stock_lrb_em()
    df2 = clean_data_by_name(df2, "lrb")
    df2.to_excel("data/利润.xlsx", index=False)

    df2["buy"] = df2.apply(lambda x: calc(x["股票简称"], x["股票代码"]), axis=1)
    df2.dropna(inplace=True, axis=0)
    df2.drop(columns=["buy"], axis=1, inplace=True)
    df2.reset_index(inplace=True)

    out_file = format("out/lrb_超跌%s.xlsx" % (time_prefix))
    df2.to_excel(out_file, index=False)
