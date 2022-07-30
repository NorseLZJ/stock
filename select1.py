"""
1、5，10，20，60 均线多头，
2、60 当天比10天之前小幅度上扬大约(2-5)百分点，
"""

import pandas as pd
from comm import *
import numpy as np
import time
import os
from redis import *

r = Redis(host="127.0.0.1", port=6379, decode_responses=True)
time_prefix = time.strftime("%Y_%m_%d", time.localtime(time.time()))
list_key = format("up_20_day_%s" % (time_prefix))


def check_ma60(df: pd.DataFrame):
    if len(df) < 20:
        return False
    last_ma60 = 0
    last_price = 0.0
    prev_ma60 = 0
    size = len(df) - 1
    count = 0
    while size >= 0:
        (_, _, _, _, close, _, _, _, _, _, _, cma60) = get_params(df, size)
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


def calc(symbol: str, price: float, code: str):
    price = float(price)
    if symbol.find("ST") == -1 and symbol.find("退") == -1 and price >= 5.0:
        code = str(code)
        # print(simple[idx])
        prefix = code[0:3]
        if prefix not in ("000", "300", "600"):
            return np.nan
        else:
            df = get_daily_data(code)
            if df is None:
                return np.nan
            df = collect_data_by_df(df)
            df.dropna(inplace=True, axis=0)
            df.reset_index(inplace=True)
            if len(df) <= 0:
                return np.nan

            (_, _, _, _, _, _, _, _, ma5, ma10, ma20, ma60) = get_params(df, len(df) - 1)
            if ma5 == 0.0 or ma10 == 0.0 or ma20 == 0.0 or ma60 == 0.0:
                return np.nan
            if ma5 < ma10 or ma5 < ma20 or ma5 < ma60:
                return np.nan
            if ma10 < ma20 or ma10 < ma60:
                return np.nan
            if ma20 < ma60:
                return np.nan
            if not (ma5 >= ma10 > ma20 > ma60):
                return np.nan
            if check_ma60(df) is False:
                return np.nan

            r.sadd(list_key, code)
            print("run :%s" % code)
            return 1
    return np.nan


if __name__ == "__main__":
    file = format("data/up20_%s.xlsx" % (time_prefix))
    # file = format("data/up20_2022_07_05.xlsx")
    if not os.path.exists(file):
        df = ak.stock_rank_xstp_ths(symbol="20日均线")
        df.to_excel(file)
    df = pd.read_excel(file, dtype=str)
    # print(df.head(30))
    df["industry"] = df.apply(lambda x: get_industry(x["股票代码"], x["股票简称"]), axis=1)
    df.dropna(inplace=True, axis=0)
    df["buy"] = df.apply(lambda x: calc(x["股票简称"], x["最新价"], x["股票代码"]), axis=1)
    df.dropna(inplace=True, axis=0)
    df.drop(columns=["Unnamed: 0", "序号"], inplace=True)
    df.sort_values(by=["industry", "最新价"], ascending=True, inplace=True)
    df.drop(columns=["buy"], axis=1, inplace=True)
    df = df.reindex(axis=0)

    out_file = format("out/up20_%s.xlsx" % (time_prefix))
    df.to_excel(out_file, index=False)
