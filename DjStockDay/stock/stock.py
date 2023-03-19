import pandas as pd
import akshare as ak
import os
import numpy as np
import talib as tl
import time
from common import *


""" stock state"""
purchase = 1
sellout = 2

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
        end_date = time.strftime("%Y-%m-%d")
        end_date = end_date.replace("-", "", -1)
        temp_df = ak.stock_zh_a_daily(symbol=symbol, end_date=end_date, adjust="qfq")
        if temp_df is None:
            return None
        temp_df.to_csv(df_file, index=False)
        temp_df.set_index("date", inplace=True)
        return temp_df


class Stock(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.run()

    def run(self):
        symbol = format_stock(symbol)
        _df = get_data(self.symbol)
        dif, dea, macd = tl.MACD(_df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
        ma5 = np.around(tl.SMA(_df["close"], timeperiod=5), 2)
        ma10 = np.around(tl.SMA(_df["close"], timeperiod=10), 2)
        ma20 = np.around(tl.SMA(_df["close"], timeperiod=20), 2)
        ma60 = np.around(tl.SMA(_df["close"], timeperiod=60), 2)

        _df.insert(loc=5, column="dif", value=np.around(dif, 2))
        _df.insert(loc=6, column="dea", value=np.around(dea, 2))
        _df.insert(loc=7, column="macd", value=np.around(macd, 2))
        _df.insert(loc=8, column="ma5", value=ma5)
        _df.insert(loc=9, column="ma10", value=ma10)
        _df.insert(loc=10, column="ma20", value=ma20)
        _df.insert(loc=11, column="ma60", value=ma60)

        _df["macd"] = _df.apply(lambda x: reset_ma(x["macd"]), axis=1)

        # _df.dropna(inplace=True)
        """重设了index后,要再次设置index是day"""
        # _df.reset_index(inplace=True)
        # _df.set_index('day', inplace=True)
        """
        计算部分
        """
        buy_list = []
        sell_list = []
        count_list = []
        profix_list = []
        prev_state = sellout
        index_list = _df.index.to_list()
        count = 0
        init_profit = 10000.0
        sub_profit = 0.0
        prev_buy_close = 0.0
        for i in range(len(_df)):
            """
            ma60需要计算的k线数最多,如果这个都有值,那别的应该都有值
            """
            if np.isnan(_df.iloc[i]["ma60"]):
                continue
            if i <= 0:
                continue
            if i >= len(_df) - 3:
                break  # 数据结束了

            prev_dif, prev_dea, prev_ma5 = g_vbs(_df.iloc[i - 1], ["dif", "dea", "ma5"])
            cur_close, cur_dif, cur_dea, cur_ma5, cur_ma20 = g_vbs(_df.iloc[i], ["close", "dif", "dea", "ma5", "ma20"])
            next_close, next_dif, next_open = g_vbs(_df.iloc[i + 1], ["close", "dif", "open"])
            next_date = index_list[i + 1]
            # 当前时间，i+1时间，i+2时间
            # 条件，判定买卖关键位置 所有的[buy,sellout]都是当前信号点的下一个节点 date,price 用的是下一个节点的
            if prev_state == sellout:
                if down_trend(cur_close, cur_ma5, prev_ma5) is True:
                    if cur_close >= cur_ma5:
                        """下跌趋势找第一次收盘价超过ma5买入"""
                        prev_state = purchase
                        _df.loc[next_date, "buy"] = next_open
                        count, sub_profit, prev_buy_close = get_buy_info(init_profit, next_open)
                else:
                    if bo_gu(prev_dif, cur_dif, next_dif):
                        prev_state = purchase
                        _df.loc[next_date, "buy"] = next_open
                        count, sub_profit, prev_buy_close = get_buy_info(init_profit, next_open)
                    elif jin_cha(prev_dif, prev_dea, cur_dif, cur_dea):
                        prev_state = purchase
                        _df.loc[next_date, "buy"] = next_open
                        count, sub_profit, prev_buy_close = get_buy_info(init_profit, next_open)
            elif prev_state == purchase:
                if down_trend(cur_close, cur_ma5, prev_ma5):
                    prev_state = sellout
                    _df.loc[next_date, "sell"] = next_open
                    init_profit, count = calc_profit(sub_profit, count, prev_buy_close, next_open)
                elif bo_fen(prev_dif, cur_dif, next_dif):
                    prev_state = sellout
                    _df.loc[next_date, "sell"] = next_open
                    init_profit, count = calc_profit(sub_profit, count, prev_buy_close, next_open)
                elif cur_close < cur_ma20:
                    prev_state = sellout
                    _df.loc[next_date, "sell"] = next_open
                    init_profit, count = calc_profit(sub_profit, count, prev_buy_close, next_open)
            """资金曲线"""
            if count != 0:
                _df.loc[next_date, "profit"] = sub_profit + (count * cur_close)
            else:
                _df.loc[next_date, "profit"] = init_profit
            # 持仓数量
            _df.loc[next_date, "count"] = count


if __name__ == "__main__":
    pass
