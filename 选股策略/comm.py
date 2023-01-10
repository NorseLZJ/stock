import akshare as ak
import talib as tl
import numpy as np
from datetime import datetime, date
import datetime as dt
import pandas as pd
import os

short_win = 12  # 短期EMA平滑天数
long_win = 26  # 长期EMA平滑天数
macd_win = 20  # DEA线平滑天数
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
# 设置命令行输出时的列对齐功能
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


def create_dir(dirs: list[str]):
    for d in dirs:
        if not os.path.exists(d):
            os.mkdir(d)


def invide_stock_code(symbol: str) -> bool:
    if len(symbol) != 6:
        return False
    if str(symbol)[0:2] not in ("00", "60", "30"):
        return False
    return True


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
    pre = code[0:2]
    if pre == "00" or pre == "30":
        return format("sz%s" % code)
    return format("sh%s" % code)


def get_daily_data(symbol: str, start_date="", end_date="") -> pd.DataFrame:
    if start_date == "" and end_date == "":
        td = dt.date.today()
        end_date = str(td).replace("-", "")
        timestamp = datetime.timestamp(datetime.now())
        dt_object = datetime.fromtimestamp(int(timestamp) - 356 * 2 * 86400)
        start_date = (str(dt_object).split(" ")[0]).replace(" ", "")

    name = get_name_akshare(symbol)
    out_file = get_stock_data_file(symbol)
    if os.path.exists(out_file):
        return pd.read_csv(out_file)
    try:
        # 拿一年左右前复权的数据
        df = ak.stock_zh_a_daily(name, start_date=start_date, end_date=end_date, adjust="qfq")
        df.to_csv(out_file, index=False)
        return df
    except Exception as e:
        print("get stock daily data[%s] err:%s" % (symbol, e))
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


def reset_macd(macd: float):
    return macd * 2


def collect_data_by_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return None

    dif, dea, macd = tl.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    ma5 = np.around(tl.SMA(df["close"], timeperiod=5), 3)
    ma10 = np.around(tl.SMA(df["close"], timeperiod=10), 3)
    ma20 = np.around(tl.SMA(df["close"], timeperiod=20), 3)
    ma60 = np.around(tl.SMA(df["close"], timeperiod=60), 3)

    df.insert(loc=6, column="dif", value=np.around(dif, 3))
    df.insert(loc=7, column="dea", value=np.around(dea, 3))
    df.insert(loc=8, column="macd", value=np.around(macd, 3))
    df.insert(loc=9, column="ma5", value=ma5)
    df.insert(loc=10, column="ma10", value=ma10)
    df.insert(loc=11, column="ma20", value=ma20)
    df.insert(loc=12, column="ma60", value=ma60)

    df["macd"] = df.apply(lambda x: reset_macd(x["macd"]), axis=1)

    df.dropna(inplace=True)
    # df.reset_index(inplace=True, drop=True)
    # df.reset_index(inplace=True)
    return df


def get_stock_data_file(symbol: str):
    return format("data/%s.csv" % (symbol))


def create_dir(dir_list):
    if len(dir_list) <= 0:
        return
    for d in dir_list:
        if not os.path.exists(d):
            os.mkdir(d)


def is_bofen(prev_dif, cur_dif, next_dif):
    if cur_dif > prev_dif and cur_dif > next_dif:
        return True
    return False


def is_bogu(prev_dif, cur_dif, next_dif):
    if cur_dif < prev_dif and cur_dif < next_dif:
        return True
    return False


def is_jincha(prev_dif, prev_dea, cur_dif, cur_dea):
    if prev_dif < prev_dea and cur_dif > cur_dea:
        return True
    return False


def g_vbs(ser: pd.Series, keys: list[str]):
    """
    get val by pd.Series
    """
    return ser[keys]


def get_before_day(day: int) -> tuple:
    timestamp = datetime.timestamp(datetime.now())
    sec = int(timestamp) - day * 86400
    dt_object = datetime.fromtimestamp(sec)
    d_str = (str(dt_object).split(" ")[0]).replace(" ", "")
    return (d_str, sec)


if __name__ == "__main__":
    s, sec = get_before_day(1)
    print(s)
    print(sec)
