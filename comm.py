import akshare as ak
import talib
import numpy as np
from datetime import datetime, date
import datetime as dt
import pandas as pd
from redis import *
import os

short_win = 12  # 短期EMA平滑天数
long_win = 26  # 长期EMA平滑天数
macd_win = 20  # DEA线平滑天数
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

r = Redis(host="127.0.0.1", port=6379, decode_responses=True)
industry_key = "industry"
failed_get_key = "failed_get_daily"


def invide_stock_code(symbol: str):
    if len(str(symbol)) != 6:
        return False
    if str(symbol)[0:2] not in ("00", "60", "30"):
        return False
    return True


def get_industry(_symbol: str, simple_name: str = ""):
    if simple_name.find("退") != -1 or simple_name.find("ST") != -1:
        return np.nan
    val = r.hget(industry_key, _symbol)
    if val is None:
        try:
            vv = ak.stock_individual_info_em(_symbol)
        except Exception as e:
            print("get industry(%s,%s) err:%s" % (_symbol, simple_name, e))
            return np.nan
        item = vv["item"]
        value = vv["value"]
        for i in range(len(item)):
            if item[i] == "行业":
                r.hset(industry_key, _symbol, value[i])
                print("new industry(%s,%s)" % (_symbol, simple_name))
                return value[i]
    else:
        return str(val)


def day_60_plus(x):
    """
    60天线是否上升趋势
    :return:
    """
    max_idx = len(x) - 1
    stop_idx = max_idx - 10
    if stop_idx > 0:
        while max_idx > stop_idx:
            if not np.isnan(x[max_idx]) and not np.isnan(x[max_idx - 1]):
                if x[max_idx] >= x[max_idx - 1]:
                    max_idx -= 1
                else:
                    return False
            else:
                return False
    return True


def get_name_akshare(code: str):
    if code[0:2] == "00" or code[0:2] == "30":  # sz
        return format("sz%s" % code)
    return format("sh%s" % code)


def get_daily_data(_symbol: str) -> pd.DataFrame:
    td = dt.date.today()
    end_date = str(td).replace("-", "")
    timestamp = datetime.timestamp(datetime.now())
    dt_object = datetime.fromtimestamp(int(timestamp) - 356 * 2 * 86400)
    start_date = (str(dt_object).split(" ")[0]).replace(" ", "")
    name = get_name_akshare(_symbol)
    out_file = get_stock_data_file(_symbol)
    val = r.hget(failed_get_key, _symbol)
    if val is not None:
        # print("redis check get stock daily data[%s] err:%s" % (_symbol, val))
        return None
    if os.path.exists(out_file):
        return pd.read_csv(out_file)
    if name == "":
        return None
    try:
        # 拿一年左右前复权的数据
        df = ak.stock_zh_a_daily(
            name, start_date=start_date, end_date=end_date, adjust="qfq"
        )
        df.to_csv(out_file, index=False)
        return df
    except Exception as e:
        print("get stock daily data[%s] err:%s" % (_symbol, e))
        r.hset(failed_get_key, _symbol, str(e))
        return None


def get_minute_data(_symbol: str, period: str):
    if period not in ("1", "5", "15", "30", "60"):
        return None
    name = get_name_akshare(_symbol)
    if name == "":
        return None
    try:
        df = ak.stock_zh_a_minute(name, period=period, adjust="qfq")
        return df
    except Exception as e:
        print("get stock minute(%s) data[%s] err:%s" % (period, _symbol, e))
        return None


def collect_data_by_json(_data):
    _df = pd.read_json(_data)
    return collect_data_by_df(_df)


def collect_data_by_df(_df) -> pd.DataFrame:
    if _df is None:
        return None
    (dif, dea, macd) = talib.MACD(
        _df["close"],
        fastperiod=short_win,
        slowperiod=long_win,
        signalperiod=macd_win,
    )
    ma5 = np.around(talib.SMA(_df["close"], timeperiod=5), 2)
    ma10 = np.around(talib.SMA(_df["close"], timeperiod=10), 2)
    ma20 = np.around(talib.SMA(_df["close"], timeperiod=20), 2)
    ma60 = np.around(talib.SMA(_df["close"], timeperiod=60), 2)
    dif = np.around(dif, 2)
    dea = np.around(dea, 2)
    macd = np.around(macd, 2)
    _df["upper"], _df["middle"], _df["lower"] = talib.BBANDS(
        _df.close.values,
        timeperiod=20,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0,
    )

    _df.insert(loc=5, column="dif", value=dif)
    _df.insert(loc=5, column="dea", value=dea)
    _df.insert(loc=5, column="macd", value=macd)
    _df.insert(loc=5, column="ma5", value=ma5)
    _df.insert(loc=5, column="ma10", value=ma10)
    _df.insert(loc=5, column="ma20", value=ma20)
    _df.insert(loc=5, column="ma60", value=ma60)

    return _df


def clean_data_by_name(df: pd.DataFrame, type: str) -> pd.DataFrame:
    if type == "zcfz":
        pass
    elif type == "lrb":
        df = df.loc[
            (df["净利润同比"] > 5.0)
            & (df["净利润同比"] < 300.0)
            & (df["股票简称"].str.find("ST") == -1)
            & (df["股票简称"].str.find("退") == -1),
            :,
        ]
        df.sort_values(
            by=["净利润同比"], inplace=True, ignore_index=True, ascending=False
        )
    elif type == "xjll":
        pass
    df.reset_index(inplace=True, drop=True)
    return df


def get_stock_data_file(symbol: str):
    return format("stock_data/%s.csv" % (symbol))


dict_reflact = {
    "date": 0,
    "open": 1,
    "high": 2,
    "low": 3,
    "close": 4,
    "ma60": 5,
    "ma20": 6,
    "ma10": 7,
    "ma5": 8,
    "macd": 9,
    "dea": 10,
    "dif": 11,
    "volume": 12,
    "money": 13,
    "upper": 14,
    "middle": 15,
    "lower": 16,
}


def k(key: str) -> int:
    v = dict_reflact.get(key)
    if v is None:
        return None
    return v


def get_stock_data_file(code: str):
    return format("data/%s.csv" % (code))
