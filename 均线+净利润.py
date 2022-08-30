"""
获取数据
    资产负债
    利润
    现金流量

默认按照最新的日期获取

*****************************

可能一个月运行一次就可以了

文档地址:
    https://www.akshare.xyz/tutorial.html

目前只做了净利润+均线选股
净利润同比为正,均线5,10,20,60多头排列

"""

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

        v = df.loc[size]
        close, cma60 = v[k("close")], v[k("ma60")]
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
    if (
        symbol.find("ST") != -1
        or symbol.find("退") != -1
        or invide_stock_code(code) is False
    ):
        return np.nan

    df = get_daily_data(code)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)
    if len(df) <= 0:
        return np.nan

    v = df.iloc[-1]
    # print(df.tail(3))
    # print(v)
    ma5, ma10, ma20, ma60 = (
        v[k("ma5")],
        v[k("ma10")],
        v[k("ma20")],
        v[k("ma60")],
    )
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

    print("手工校验下:%s" % code)
    return 1


if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")

    # df = ak.stock_zcfz_em()
    # df = clean_data(df, "zcfz")
    # df.to_excel("data/资产负债.xlsx", index=False)

    df2 = ak.stock_lrb_em()
    df2 = clean_data_by_name(df2, "lrb")
    df2.to_excel("data/利润.xlsx", index=False)

    df2["buy"] = df2.apply(lambda x: calc(x["股票简称"], x["股票代码"]), axis=1)
    df2.dropna(inplace=True, axis=0)
    df2.drop(columns=["buy"], axis=1, inplace=True)
    df2.reset_index(inplace=True)

    out_file = format("out/lrb%s.xlsx" % (time_prefix))
    df2.to_excel(out_file, index=False)

    # df3 = ak.stock_xjll_em()
    # df3 = clean_data(df3, "xjll")
    # df3.to_excel("data/现金流量.xlsx", index=False)
