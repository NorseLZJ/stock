"""
data
"""
import pandas as pd
import akshare as ak
import os
import numpy as np
import talib as tl
import time


# Create your views here.
def format_stock(symbol: str):
    prefix = symbol[0:2]
    if prefix == "00":
        return format("sz%s" % symbol)
    if prefix == "60":
        return format("sh%s" % symbol)
    if prefix == "30":
        return format("sz%s" % symbol)


def get_data(symbol: str):
    if os.path.exists("data") is False:
        os.mkdir("data")

    if os.path.exists("trades") is False:
        os.mkdir("trades")

    df_file = format("data/%s.csv" % symbol)
    if os.path.exists(df_file):
        stat = os.stat(df_file)
        sub_sec = int(time.time() - stat.st_ctime)
        if sub_sec > (3600 * 4):
            os.remove(df_file)

    if os.path.exists(df_file):
        temp_df = pd.read_csv(df_file)
        temp_df.set_index("date", inplace=True)
        return temp_df
    else:
        # temp_df = ak.stock_zh_a_daily(symbol=symbol, start_date='20150101', adjust='qfq')
        temp_df = ak.stock_zh_a_daily(symbol=symbol, start_date="20220101", adjust="qfq")
        if temp_df is None:
            return None
        temp_df.to_csv(df_file, index=False)
        temp_df.set_index("date", inplace=True)
        return temp_df


def reset_ma(macd: float):
    return macd * 2


def bo_fen(prev_dif, cur_dif, next_dif):
    if cur_dif > prev_dif and cur_dif > next_dif:
        return True
    return False


def bo_gu(prev_dif, cur_dif, next_dif):
    if cur_dif < prev_dif and cur_dif < next_dif:
        return True
    return False


def jin_cha(prev_dif, prev_dea, cur_dif, cur_dea):
    if prev_dif < prev_dea and cur_dif > cur_dea:
        return True
    return False


def g_vbs(ser: pd.Series, keys: list):
    """
    get val by pd.Series
    """
    return ser[keys]


def down_trend(cur_close, cur_ma5, prev_ma5) -> bool:
    """
    Parameters
    ----------
    cur_close :当日收盘价
    cur_ma5 :当日ma5
    prev_ma5 : 前一日ma5
    Returns
    -------
    true:下降趋势
    false:非下降趋势
    """

    return cur_close <= cur_ma5 < prev_ma5


def get_buy_info(profit: float, close: float) -> tuple:
    """
    获取买入信息,可以买入多少股，100的整数倍
    Parameters
    ----------
    profit:资金总额
    close:买入价格

    Returns
    -------
    int:购买数量，
    float:剩余资金
    bool:成功返回true，第一次不需要计入数量，第二次才计入
    """
    one_hand_profit = close * 100
    hand_num = int(profit / one_hand_profit)
    if hand_num <= 0:
        return 0, profit, close

    sub_profit = profit - (hand_num * 100 * close)
    return hand_num * 100, sub_profit, close


def calc_profit(sub_profit: float, count: int, prev_close: float, cur_close: float) -> tuple:
    """
    ----------
    sub_profit : 剩余的资金
    count : 股票数量
    prev_close :  买入价格
    cur_close : 卖出价格
    Returns
        float: 剩余资金
        int:返回 0 重写股票数量
    -------
    """
    # 扣手续费还没写
    profit = sub_profit + (cur_close * count)
    return profit, 0


def calc_profit(sub_profit: float, count: int, prev_close: float, cur_close: float) -> tuple:
    """
    ----------
    sub_profit : 剩余的资金
    count : 股票数量
    prev_close :  买入价格
    cur_close : 卖出价格
    Returns
        float: 剩余资金
        int:返回 0 重写股票数量
    -------
    """
    # 扣手续费还没写
    profit = sub_profit + (cur_close * count)
    return profit, 0
