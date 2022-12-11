from re import L
import pandas as pd
from comm import *


"""
找出 一年中前3季度的利润是负的,第四季度是正的
先拿到4季度的净利润
"""

lrb_date_map_2020 = {
    1: "20200331",
    2: "20200630",
    3: "20200930",
    4: "20201231",
}

lrb_date_map_2021 = {
    1: "20210331",
    2: "20210630",
    3: "20210930",
    4: "20211231",
}

all_stock_lrb = {}


class Runner(object):
    def __init__(self, lrb_dict, year) -> None:
        self.lrb_dict = lrb_dict
        self.all_stock_lrb = {}
        self.stock = {}
        self.run(year)

    def set_to_dict(self, x, key):
        code = x["股票代码"]
        v1 = self.all_stock_lrb.get(code)
        if v1 is None:
            self.all_stock_lrb[code] = {key: x["净利润"]}
            return
        v1[key] = x["净利润"]

    def get_stock(self):
        return self.stock

    def get_save_file(self, key, year):
        val = self.lrb_dict.get(key)
        if val is None:
            return None, None
        return val, format("data/lrb_%s_%s.csv" % (year, val))

    def run(self, year):
        for (key, _) in self.lrb_dict.items():
            date, outfile = self.get_save_file(key, year)
            if date is None or outfile is None:
                return
            if os.path.exists(outfile):
                df = pd.read_csv(outfile, dtype={"股票代码": str})
                df.apply(lambda x: self.set_to_dict(x, key), axis=1)
            else:
                df = ak.stock_lrb_em(date=date)
                df.apply(lambda x: self.set_to_dict(x, key), axis=1)
                df.to_csv(outfile)

        for (code, val) in self.all_stock_lrb.items():
            m1 = val.get(1)
            m2 = val.get(2)
            m3 = val.get(3)
            m4 = val.get(4)
            if None in (m1, m2, m3, m4):
                continue
            if m1 < 0 and m2 < 0 and m3 < 0 and m4 > 0:
                if code[0:3] == "688":
                    continue
                self.stock[code] = 1


if __name__ == "__main__":
    create_dir(["data", "out"])

    lrb_2020 = Runner(lrb_date_map_2020, "2020").get_stock()
    lrb_2021 = Runner(lrb_date_map_2021, "2021").get_stock()
    code_list = []
    industry_list = []
    for (k, _) in lrb_2020.items():
        if lrb_2021.get(k) is None:
            continue
        code_list.append(k)
        industry_list.append(get_industry(k, ""))
    df = pd.DataFrame({"code": code_list, "industry": industry_list})
    df.to_csv("temp.csv")
