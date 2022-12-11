"""
条件
    1.轴线金叉
"""
import pandas as pd
from comm import *
import time
import jqdatasdk as jq

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

time_prefix = time.strftime("%Y_%m_%d", time.localtime(time.time()))


def calc(code: str):
    df = jq.get_bars(
        code,
        100,
        unit="1w",
        fields=["open", "high", "low", "close", "volume", "money"],
        include_now=True,
    )
    if df is None:
        return np.nan

    df = collect_data_by_df(df)
    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)

    if len(df) < 2:
        return np.nan
    l1_dif = df.iloc[-1]["dif"]
    l1_dea = df.iloc[-1]["dea"]

    l2_dif = df.iloc[-2]["dif"]
    l2_dea = df.iloc[-2]["dea"]

    # 周线级别刚刚金叉
    if l1_dif > l1_dea and l2_dif >= l2_dea:
        print(code)
        return 1
    return np.nan


if __name__ == "__main__":
    # 自行注册聚宽账号填入
    jq.auth("", "")
    create_dir(["data", "out"])

    """test """
    # print(calc(jq.normalize_code("601818")))
    """test """

    df = ak.stock_lrb_em()
    df = df.loc[
        (df["净利润同比"] > 5.0)
        & (df["净利润同比"] < 300.0)
        & (df["股票简称"].str.find("ST") == -1)
        & (df["股票简称"].str.find("退") == -1),
        :,
    ]

    df["signle"] = df.apply(
        lambda x: calc(jq.normalize_code(x["股票代码"])), axis=1
    )
    df["industry"] = df.apply(lambda x: get_industry(x["股票代码"], ""), axis=1)
    df.sort_values(
        by=["industry", "净利润同比"],
        inplace=True,
        ignore_index=True,
        ascending=False,
    )

    df.dropna(inplace=True, axis=0)
    df.reset_index(inplace=True, drop=True)

    out_file = format("out/周线金叉_%s.xlsx" % (time_prefix))
    df.to_excel(out_file, index=False)
