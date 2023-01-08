import talib
import pandas as pd
import numpy
from redis import *

short_win = 12  # 短期EMA平滑天数
long_win = 26  # 长期EMA平滑天数
macd_win = 20  # DEA线平滑天数
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)

def is_jc(_dif, _dea):  # 金叉
    if _dif >= _dea:
        return "buy"
    return "sellout"


def get_params(_df, idx):
    if idx > len(_df):
        return None
    return (
        df.loc[idx]['date'],
        df.loc[idx]['open'],
        df.loc[idx]['high'],
        df.loc[idx]['low'],
        df.loc[idx]['close'],
        df.loc[idx]['dif'],
        df.loc[idx]['dea'],
        df.loc[idx]['macd'],
        df.loc[idx]['ma5'],
        df.loc[idx]['ma10'],
        df.loc[idx]['ma20'],
        df.loc[idx]['ma60'],
    )


def collect_data(_data):
    _df = pd.read_json(_data)
    (dif, dea, macd) = talib.MACD(_df['close'], fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
    ma5 = numpy.around(talib.SMA(_df['close'], timeperiod=5), 2)
    ma10 = numpy.around(talib.SMA(_df['close'], timeperiod=10), 2)
    ma20 = numpy.around(talib.SMA(_df['close'], timeperiod=20), 2)
    ma60 = numpy.around(talib.SMA(_df['close'], timeperiod=60), 2)
    dif = numpy.around(dif, 2)
    dea = numpy.around(dea, 2)
    macd = numpy.around(macd, 2)

    _df.insert(loc=5, column='dif', value=dif)
    _df.insert(loc=5, column='dea', value=dea)
    _df.insert(loc=5, column='macd', value=macd)
    _df.insert(loc=5, column='ma5', value=ma5)
    _df.insert(loc=5, column='ma10', value=ma10)
    _df.insert(loc=5, column='ma20', value=ma20)
    _df.insert(loc=5, column='ma60', value=ma60)

    _df['signal'] = _df.apply(lambda x: is_jc(x['dif'], x['dea']), axis=1)
    return _df


if __name__ == "__main__":
    keys = r.keys('*')
    key = keys[0]
    data = r.get(key)
    df = collect_data(data)
    # (date, _, _, _, close, dif, dea, macd, ma5, ma10, ma20, ma60) = get_params(df, len(df) - 1)
    x = get_params(df, len(df) - 1)
    # print(x)
    print(df.tail(30))
