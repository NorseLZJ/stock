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
from comm import *
from lrb import *
import time

time_prefix = time.strftime("%Y_%m_%d", time.localtime(time.time()))

pd.set_option("display.max_rows", 1000)
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
# 设置命令行输出时的列对齐功能
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


def calc(code: str):
    if invide_stock_code(code) is False:
        return np.nan

    df = get_daily_data(code)
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True)
    if len(df) <= 0:
        return np.nan

    max_idx = len(df) - 1
    if max_idx < 150:  # 股票日交易日太少
        return np.nan

    count = 0
    found = False
    """
    有150个交易日估价都在60天均线下方，理解为超跌
    """
    while max_idx >= 0:
        t_val, t_ma60 = g_vbs(df.iloc[max_idx], ["close", "ma60"])
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
    create_dir(["data", "out"])

    df = ak.stock_lrb_em()
    df = CleanLRB(df)

    df["buy"] = df.apply(lambda x: calc(x["股票代码"]), axis=1)
    df.dropna(inplace=True, axis=0)
    df.drop(columns=["buy"], axis=1, inplace=True)

    DelLRBColumn(df)
    out_file = format("out/lrb_超跌%s.xlsx" % (time_prefix))
    df.to_excel(out_file, index=False)
