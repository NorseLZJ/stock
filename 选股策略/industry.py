# /usr/bin/python3

"""
行业获取,保存
"""
import numpy as np
import pandas as pd
import akshare as ak
import os

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

file = "data/industry.csv"
if os.path.exists("data") is False:
    os.mkdir("data")


class Industry(object):
    def __init__(self) -> None:
        self._key = []
        self._val = []
        self._dict = {}
        if os.path.exists(file):

            def fill_Industry(k, v):
                self._key.append(k)
                self._val.append(v)
                self._dict[k] = v

            df = pd.read_csv(file, dtype=str)
            df.apply(lambda x: fill_Industry(x["code"], x["industry"]), axis=1)

    def GetIndustry(self, symbol, name=""):
        if name.find("退") != -1 or name.find("ST") != -1:
            return np.nan
        try:
            if self._dict.get(symbol) is not None:
                return self._dict.get(symbol)

            vv = ak.stock_individual_info_em(symbol)
            self._key.append(symbol)
            self._val.append(vv.loc[2]["value"])
            self._dict[symbol] = vv.loc[2]["value"]
            self.Save()
            return vv.loc[2]["value"]
        except Exception as e:
            print("Get Industry(%s,%s) err:%s" % (symbol, name, e))
            return np.nan

    def Save(self):
        df = pd.DataFrame.from_dict(data={"code": self._key, "industry": self._val})
        df.to_csv(file, index=False)


if __name__ == "__main__":
    i = Industry()
    i.GetIndustry("002424")
    i.GetIndustry("601611")
    i.GetIndustry("600568")
    i.GetIndustry("000001")
