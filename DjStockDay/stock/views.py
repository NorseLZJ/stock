import pandas as pd
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import akshare as ak
import os
import numpy as np
import talib as tl
import redis
import time

r = redis.Redis(host="127.0.0.1", port=6379)

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
        temp_df = ak.stock_zh_a_daily(symbol=symbol, start_date='20220101', adjust='qfq')
        if temp_df is None:
            return None
        temp_df.to_csv(df_file, index=False)
        temp_df.set_index("date", inplace=True)
        return temp_df


def __reset_ma(macd: float):
    return macd * 2


def __bo_fen(prev_dif, cur_dif, next_dif):
    if cur_dif > prev_dif and cur_dif > next_dif:
        return True
    return False


def __bo_gu(prev_dif, cur_dif, next_dif):
    if cur_dif < prev_dif and cur_dif < next_dif:
        return True
    return False


def __jin_cha(prev_dif, prev_dea, cur_dif, cur_dea):
    if prev_dif < prev_dea and cur_dif > cur_dea:
        return True
    return False


def __g_vbs(ser: pd.Series, keys: []):
    """
    get val by pd.Series
    """
    return ser[keys]


def __down_trend(cur_close, cur_ma5, prev_ma5) -> bool:
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


def __get_buy_info(profit: float, close: float) -> (int, float, float):
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


def __calc_profit(sub_profit: float, count: int, prev_close: float, cur_close: float) -> (float, int):
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


def __calc_buy_sell(_df: pd.DataFrame):
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

    _df["macd"] = _df.apply(lambda x: __reset_ma(x["macd"]), axis=1)

    # _df.dropna(inplace=True)
    '''重设了index后,要再次设置index是day'''
    # _df.reset_index(inplace=True)
    # _df.set_index('day', inplace=True)
    '''
    计算部分
    '''
    _df[['buy', 'sell', 'profit']] = 0.0
    _df[['count']] = 0
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

        prev_dif, prev_dea, prev_ma5 = (__g_vbs(_df.iloc[i - 1], ["dif", "dea", "ma5"]))
        cur_close, cur_dif, cur_dea, cur_ma5, cur_ma20 = (__g_vbs(_df.iloc[i], ["close", "dif", "dea", "ma5", "ma20"]))
        next_close, next_dif, next_open = (__g_vbs(_df.iloc[i + 1], ["close", "dif", "open"]))
        next_date = index_list[i + 1]
        # 当前时间，i+1时间，i+2时间
        # 条件，判定买卖关键位置 所有的[buy,sellout]都是当前信号点的下一个节点 date,price 用的是下一个节点的
        if prev_state == sellout:
            if __down_trend(cur_close, cur_ma5, prev_ma5) is True:
                if cur_close >= cur_ma5:
                    """下跌趋势找第一次收盘价超过ma5买入"""
                    prev_state = purchase
                    _df.loc[next_date, 'buy'] = next_open
                    count, sub_profit, prev_buy_close = __get_buy_info(init_profit, next_open)
            else:
                if __bo_gu(prev_dif, cur_dif, next_dif):
                    prev_state = purchase
                    _df.loc[next_date, 'buy'] = next_open
                    count, sub_profit, prev_buy_close = __get_buy_info(init_profit, next_open)
                elif __jin_cha(prev_dif, prev_dea, cur_dif, cur_dea):
                    prev_state = purchase
                    _df.loc[next_date, 'buy'] = next_open
                    count, sub_profit, prev_buy_close = __get_buy_info(init_profit, next_open)
        elif prev_state == purchase:
            if __down_trend(cur_close, cur_ma5, prev_ma5):
                prev_state = sellout
                _df.loc[next_date, 'sell'] = next_open
                init_profit, count = __calc_profit(sub_profit, count, prev_buy_close, next_open)
            elif __bo_fen(prev_dif, cur_dif, next_dif):
                prev_state = sellout
                _df.loc[next_date, 'sell'] = next_open
                init_profit, count = __calc_profit(sub_profit, count, prev_buy_close, next_open)
            elif cur_close < cur_ma20:
                prev_state = sellout
                _df.loc[next_date, 'sell'] = next_open
                init_profit, count = __calc_profit(sub_profit, count, prev_buy_close, next_open)
        """资金曲线"""
        if count != 0:
            _df.loc[next_date, 'profit'] = sub_profit + (count * cur_close)
        else:
            _df.loc[next_date, 'profit'] = init_profit
        # 持仓数量
        _df.loc[next_date, 'count'] = count


@csrf_exempt
def stock(req):
    if req.method == "GET":
        return render(req, "index2.html")
    result = {
        "data": "",
        "result": False,
    }
    symbol = req.POST.get('ID')
    if symbol is None or symbol == '' or len(symbol) < 6:
        return JsonResponse(result)
    symbol = format_stock(symbol)
    resp = r.exists(symbol)
    if resp != 0:
        val = r.get(symbol).decode()
        return JsonResponse({"data": val, "result": True})

    _df = get_data(symbol=symbol)
    if _df is None:
        return HttpResponse("内部错误")
    __calc_buy_sell(_df)
    data = []
    _df.drop(inplace=True, columns=['ma5', 'ma10', 'ma20', 'ma60', 'dif', 'dea', 'macd', 'volume'])

    _df[['open', 'close', 'high', 'low', 'buy', 'sell', 'profit']] = np.round(
        _df[['open', 'close', 'high', 'low', 'buy', 'sell', 'profit']].astype(float), 2)

    _df.reset_index().apply(
        lambda x: data.append(
            [
                str(x["date"]).replace("-", "/"),
                str(x["open"]),
                str(x["close"]),
                str(x["low"]),
                str(x["high"]),
                str(x["buy"]),
                str(x["sell"]),
                str(x["profit"]),
            ]
        ),
        axis=1,
    )

    r.setex(symbol, 60 * 60, str(data))

    val = {
        "data": str(data),
        "result": True,
    }
    return JsonResponse(val)


def index(request):
    return render(request, "index.html")


def index2(request):
    return render(request, "layout.html")


if __name__ == "__main__":
    df = get_data("sz000001")
    __calc_buy_sell(df)
    df.to_excel("temp.xlsx")
    """
    df.reset_index().apply(
        lambda x: val.append(
            [
                str(x["day"]).replace("-", "/"),
                str(np.round(x["open"], 2)),
                str(np.round(x["close"], 2)),
                str(np.round(x["low"], 2)),
                str(np.round(x["high"], 2)),
                str(x["buy"]),
                str(x["sell"]),
            ]
        ),
        axis=1,
    )
    df.drop(inplace=True, columns=['ma5', 'ma10', 'ma20', 'ma60', 'dif', 'dea', 'macd', 'volume'])
    df[['open', 'close', 'high', 'low', 'buy', 'sell']] = np.round(
        df[['open', 'close', 'high', 'low', 'buy', 'sell']].astype(float), 2)
    df.to_csv("test.csv")
    """
