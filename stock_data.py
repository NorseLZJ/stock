"""
get date from network
"""
import akshare as ak
import pandas as pd
from select_move import *
from comm import *

""" stock state"""
purchase_ing = 1
sellout_ing = 2


class SubPrice(object):
    def __init__(self, price1, date1, price2, date2):
        self.price1 = price1
        self.date1 = date1
        self.price2 = price2
        self.date2 = date2

    def bill_info(self, is_add, val):
        if is_add == 0:
            return format("%s %s [in:%f out:%f] +%d\n" % (self.date1, self.date2, self.price1, self.price2, val))
        else:
            return format("%s %s [in:%f out:%f] %d\n" % (self.date1, self.date2, self.price1, self.price2, val))


class SixtyMinter(object):
    def __init__(self, date, state, dif, price, next_date):
        self.date = date
        self.state = state
        self.dif = dif
        self.price = price
        self.next_date = next_date

    def info_six_minter(self):
        if self.state == purchase_ing:
            return format("%s  买入持有   %f\n" % (self.date, self.dif)), self.state, self.price, self.date, self.next_date
        else:
            return format("%s  卖出空仓   %f\n" % (self.date, self.dif)), self.state, self.price, self.date, self.next_date
        return "-" * 10


class StockData(object):
    def __init__(self, code: str):
        self.code = code
        self.sixtyList = []
        self.content = ""
        self.bill_cent = ""
        self.opt_list = []
        self.df = None

        # 日线数据
        self.minute60()
        self.info_list()
        self.info_list_rever()

    def minute60(self):
        self.df = get_minute_data(self.code, "60")
        self.df = collect_data_by_df(self.df)
        self.df.dropna(inplace=True)
        self.df.reset_index(inplace=True)
        print(self.df.head(10))
        for i in range(len(self.df)):
            if i <= 0 or i > (len(self.df) - 2):
                continue  # start or end

            pv = get_params_by_key(self.df, ["close", "dif", "dea"], i - 1)
            pclose, pdif, pdea = (pv[0], pv[1], pv[2])
            cv = get_params_by_key(self.df, ["close", "dif", "dea", "ma60", "day"], i)
            cclose, cdif, cdea, cma60, cday = (cv[0], cv[1], cv[2], cv[3], cv[4])
            nv = get_params_by_key(self.df, ["close", "dif", "dea", "day"], i + 1)
            nclose, ndif, ndea, nday = (nv[0], nv[1], nv[2], nv[3])

            if cdif > pdif and cclose >= cma60:
                """当前大于前一个，谷底，操作后一个到后一个+1"""
                self.sixtyList.append(SixtyMinter(cday, purchase_ing, cdif, nclose, nday))
            elif cdif < pdif:
                """当前小于前一个,谷顶"""
                self.sixtyList.append(SixtyMinter(cday, sellout_ing, cdif, nclose, nday))

    def info_list_rever(self):
        txt = ""
        for v in reversed(self.sixtyList):
            content, _, _, _, _ = v.info_six_minter()
            txt += content

        self.content = txt

    def info_list(self):
        prev_state = 0
        price1 = 0
        for v in self.sixtyList:
            _, state, price, c_date, _ = v.info_six_minter()

            if prev_state == 0:
                prev_state = state
                continue

            # 处理持仓过程
            if prev_state == sellout_ing and state == purchase_ing:  # 前一个状态是卖出，现在需要买入
                price1 = price
                date1 = c_date
            elif prev_state == purchase_ing and state == sellout_ing:
                if price1 != 0 and date1 != "":
                    self.opt_list.append(SubPrice(price1, date1, price, c_date))
            prev_state = state

        # 买卖操作收益
        bill_txt = ""
        all_money = 0
        for v in self.opt_list:
            val = v.price2 - v.price1
            count = int(10000 / v.price1)
            count = int(count / 100) * 100
            if val > 0:  # 赚钱
                add_money = (val * count) - 10  # 10手续费等
                bill_txt += v.bill_info(0, add_money)
                all_money += add_money
            else:  # 亏钱
                sub_money = (val * count) - 10  # 10手续费等
                bill_txt += v.bill_info(-1, sub_money)
                all_money += sub_money
        self.bill_cent = bill_txt
        self.bill_cent += format("总收益:%d" % all_money)

    def get_content(self):
        return (self.content, self.bill_cent)


if __name__ == "__main__":
    s = StockData("002424")
    (opt, bill) = s.get_content()
    print(opt)
    print(bill)
