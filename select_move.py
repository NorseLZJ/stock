from comm import *
import numpy as np
from datetime import datetime as dt


def check_avg(_symbol: str) -> bool:
    df = get_daily_data(_symbol)
    if df is None:
        return False
    cp_df = collect_data_by_df(df)
    cp_df.dropna(inplace=True, axis=0)
    cp_df.reset_index(inplace=True)
    if len(cp_df) <= 0:
        return False

    (_, _, _, _, close, _, _, _, _, _, ma20, ma60, _) = get_params(cp_df, len(cp_df) - 1)

    # TODO 当前股价在60,20天均线以上 但是超过60均线不足5%
    if ma60 != 0 and ma20 != 0:
        if (close > ma60) and (close > ma20):
            ret = (close - ma60) / ma60 * 100
            if ret < 5.0:
                return True
    return False


class Stock(object):
    def __init__(self, _symbol: str, _name: str, _price):
        self.symbol = _symbol
        self.name = _name
        self.price = _price

    def info(self):
        return format("\t%s %s %f\n" % (self.symbol, self.name, self.price))


def calc(symbol: str, price: float, code: str):
    if symbol.find("ST") == -1 and symbol.find("退市") == -1 and price >= 5.0:
        code = str(code)
        # print(simple[idx])
        prefix = code[0:3]
        if prefix in ("000", "300", "600") and check_avg(code) is True:
            print("run :%s" % code)
            return 1
    return np.nan


if __name__ == "__main__":
    v = ak.stock_rank_xstp_ths(symbol="20日均线")
    v["buy"] = v.apply(lambda x: calc(x["股票简称"], x["最新价"], x["股票代码"]), axis=1)
    v["industry"] = v.apply(lambda x: get_industry(x["股票代码"]), axis=1)
    v.dropna(inplace=True, axis=0)
    v.to_excel("today.xlsx", index=False)
