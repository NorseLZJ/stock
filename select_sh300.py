import os.path
import akshare as ak
import talib
import numpy
from datetime import datetime, date
import datetime as dt
import pandas as pd
from comm import *


def check_avg(_symbol: str) -> bool:
    td = dt.date.today()
    end_date = str(td).replace('-', '')
    timestamp = datetime.timestamp(datetime.now())
    dt_object = datetime.fromtimestamp(int(timestamp) -
                                       240 * 86400)  # 100天左右的数据
    start_date = (str(dt_object).split(' ')[0]).replace(' ', '')

    name = get_name_akshare(_symbol)
    if name == '':
        return False

    # print('get code %s\n' % name)
    try:
        df = ak.stock_zh_a_daily(name,
                                 start_date=start_date,
                                 end_date=end_date)
    except Exception as e:
        print("get stock[%s] err:%s" % (_symbol, e))
        return

    c_date = df['date']
    c_close = df['close']
    prices = []
    for i in range(len(c_date)):
        prices.append(float(c_close[i]))

    xx = numpy.array(prices)
    all_nan = True
    for vv in xx:
        if not numpy.isnan(vv):
            all_nan = False
            break
    if all_nan is True:
        return False

    prices = numpy.around(xx, 2)
    avg5 = talib.SMA(xx, timeperiod=5)
    avg10 = talib.SMA(xx, timeperiod=10)
    avg20 = talib.SMA(xx, timeperiod=20)
    avg60 = talib.SMA(xx, timeperiod=60)

    avg5 = numpy.around(avg5, 2)
    avg10 = numpy.around(avg10, 2)
    avg20 = numpy.around(avg20, 2)
    avg60 = numpy.around(avg60, 2)
    i = len(avg5) - 1
    a5 = avg5[i] if not numpy.isnan(avg5[i]) else 0
    a10 = avg10[i] if not numpy.isnan(avg10[i]) else 0
    a20 = avg20[i] if not numpy.isnan(avg20[i]) else 0
    a60 = avg60[i] if not numpy.isnan(avg60[i]) else 0
    cur_price = prices[len(prices) - 1]

    # TODO 当前股价在60,20天均线以上 但是超过60均线不足5%
    if a60 != 0 and a20 != 0 and a10 != 0 and a5 != 0:
        if (cur_price > a60) and (cur_price > a20):
            ret = ((cur_price - a60) / a60 * 100)
            if ret < 5.0:
                return True
    return False


def get_day_data(_code: str) -> bool:
    td = dt.date.today()
    end_date = str(td).replace('-', '')
    timestamp = datetime.timestamp(datetime.now())
    dt_object = datetime.fromtimestamp(int(timestamp) -
                                       240 * 86400)  # 100天左右的数据
    start_date = (str(dt_object).split(' ')[0]).replace(' ', '')

    name = get_name_akshare(_code)
    if name == '':
        return False

    df = ak.stock_zh_a_daily(name, start_date=start_date, end_date=end_date)
    c_date = df['date']
    c_close = df['close']
    prices = []
    for i in range(len(c_date)):
        # print(c_date[idx], ' ', c_close[idx])
        prices.append(float(c_close[i]))

    x = numpy.array(prices)
    all_nan = True
    for v in x:
        if not numpy.isnan(v):
            all_nan = False
            break
    if all_nan is True:
        return False

    prices = numpy.around(x, 2)
    avg5 = talib.SMA(x, timeperiod=5)
    avg10 = talib.SMA(x, timeperiod=10)
    avg20 = talib.SMA(x, timeperiod=20)
    avg60 = talib.SMA(x, timeperiod=60)

    avg5 = numpy.around(avg5, 2)
    avg10 = numpy.around(avg10, 2)
    avg20 = numpy.around(avg20, 2)
    avg60 = numpy.around(avg60, 2)
    if day_60_plus(avg60) is False:
        return False
    i = len(avg5) - 1
    a5 = avg5[i] if not numpy.isnan(avg5[i]) else 0
    a10 = avg10[i] if not numpy.isnan(avg10[i]) else 0
    a20 = avg20[i] if not numpy.isnan(avg20[i]) else 0
    a60 = avg60[i] if not numpy.isnan(avg60[i]) else 0
    cur_price = prices[len(prices) - 1]

    # TODO 当前股价在60,20天均线以上
    if a60 != 0 and a20 != 0 and a10 != 0 and a5 != 0:
        if (cur_price > a60) and (cur_price > a20):
            return True
    return False


class Stock(object):

    def __init__(self, _symbol: str, _name: str, _price):
        self.symbol = _symbol
        self.name = _name
        self.price = _price

    def info(self):
        return format("\t%s %s %f\n" % (self.symbol, self.name, self.price))


def get_by_fund_list(_symbol: str):
    xx = ak.stock_report_fund_hold_detail(symbol=_symbol)
    ak.fund_portfolio_hold_em()
    codes = []
    names = []

    for idx in range(len(xx)):
        codes.append(str(xx.iloc[idx]['股票代码']).split('.')[0])
        names.append(str(xx.iloc[idx]['股票简称']))
    ret = pd.DataFrame({"stock_code": codes, "stock_simple": names})
    return ret


if __name__ == "__main__":
    #if not os.path.exists("cache"):
    #    os.mkdir("cache")

    industry_map = {}
    xx = get_by_fund_list('510300')
    print(len(xx))

    for i in range(len(xx)):
        code = xx.iloc[i]['stock_code']
        prefix = code[0:3]
        name = xx.iloc[i]['stock_simple']
        # print('run code(%s)' % code)
        if prefix in ('000', '300', '600') and check_avg(code) is True:
            industry = get_industry(code)
            if industry_map.get(industry) is None:
                industry_map[industry] = [Stock(name, code, 0)]
            else:
                industry_map[industry].append(Stock(name, code, 0))
    all_txt = ''
    for k, v in industry_map.items():
        cent = ''
        for x in v:
            cent += x.info()
        all_txt += format("%s ---------------\n%s" % (k, cent))
    with open('cache.txt', 'w', encoding='utf8') as f:
        f.write(all_txt)
