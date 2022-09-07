import pandas as pd
from comm import *
import jqdatasdk as jq
import os
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib as mpl

""" stock state"""
purchase = 1
sellout = 2


class Trade(object):
    def __init__(self, date, dif, price, msg):
        self.b_date = date
        self.s_date = ""
        self.b_dif = dif
        self.s_dif = 0.0
        self.b_price = price
        self.s_price = 0.0
        self.b_msg = msg
        self.s_msg = ""
        self.profit = 0.0

    def sellout(self, price, msg, date, dif):
        self.s_price = price
        self.s_msg = msg
        self.s_date = date
        self.s_dif = dif

    def info_trade(self):
        return format("")


def buy_set(df_date: str, price: float, trades: list[Trade]):
    for i in trades:
        if i.b_date == df_date:
            return price * 0.98
    return np.nan


def sell_set(df_date: str, price: float, trades: list[Trade]):
    for i in trades:
        if i.s_date == df_date:
            return price * 1.02
    return np.nan


class StockData(object):
    def __init__(self, code: str, draw: False):
        self.code = code
        self.trades: list[Trade] = []
        self.bill = ""  # 账单
        self.allProfit = 0.0
        # 1000个60分钟k线,根据需要自己修改
        self.df: pd.DataFrame = jq.get_bars(
            self.code,
            1000,
            unit="60m",
            fields=["date", "open", "high", "low", "close", "volume", "money"],
            include_now=True,
        )
        if self.df is None:
            self.opt = format("can't find stock code:%s" % self.code)
            return False

        self.df = collect_data_by_df(self.df)
        self.df.dropna(inplace=True)
        self.df.reset_index(inplace=True)
        self.df.drop(labels="index", inplace=True, axis=1)
        self.calc()
        self.bill_calc()

        if draw is True:
            self.mpf_draw()

    def mpf_draw(self):
        df = self.df

        df["buy"] = df.apply(lambda x: buy_set(x["date"], x["close"], self.trades), axis=1)
        df["sell"] = df.apply(lambda x: sell_set(x["date"], x["close"], self.trades), axis=1)

        df.rename(
            columns={
                "date": "Date",
                "open": "Open",
                "close": "Close",
                "high": "High",
                "low": "Low",
                "volume": "Volume",
                "money": "Money",
            },
            inplace=True,
        )

        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index(["Date"], inplace=True)  # 将日期设置为索引

        df["Open"] = df["Open"].astype("float")
        df["Close"] = df["Close"].astype("float")
        df["High"] = df["High"].astype("float")
        df["Low"] = df["Low"].astype("float")
        df["Volume"] = df["Volume"].astype("float")

        df.to_csv("test.csv")
        df = pd.read_csv("test.csv")
        # print(df)
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index(["Date"], inplace=True)  #

        # macd
        exp12 = df["Close"].ewm(span=12, adjust=False).mean()
        exp26 = df["Close"].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        # mav=(10)
        kwargs = dict(
            mav=(10, 5, 120),
            type="candle",
            volume=True,
            title=self.code + "的K线图",
            ylabel="股票价格",
            ylabel_lower="成交量",
            figratio=(15, 10),
            figscale=5,
        )
        mc = mpf.make_marketcolors(
            up="red",
            down="green",
            edge="i",
            wick="i",
            volume="in",
            inherit=True,
        )
        mpfStyle = mpf.make_mpf_style(
            gridaxis="both",
            gridstyle="--",
            y_on_right=False,
            marketcolors=mc,
            rc={"font.family": "SimHei"},
        )
        # mpl.rcParams['axes.prop_cycle']=cycler(color=['dodgerblue', 'deeppink', 'navy', 'teal', 'maroon', 'darkorange', 'indigo'])
        # mpl.rcParams['lines.linewidth']=.5

        ##加入买和卖
        # for i
        add_plot = [
            mpf.make_addplot(df["buy"], scatter=True, markersize=80, marker="^", color="r"),
            mpf.make_addplot(df["sell"], scatter=True, markersize=80, marker="v", color="g"),
            # mpf.make_addplot(exp12, type='line', color='y'),
            # mpf.make_addplot(exp26, type='line', color='r'),
            mpf.make_addplot(
                histogram,
                type="bar",
                width=0.7,
                panel=2,
                color="dimgray",
                alpha=1,
                secondary_y=False,
            ),
            mpf.make_addplot(macd, panel=2, color="fuchsia", secondary_y=True),
            mpf.make_addplot(signal, panel=2, color="b", secondary_y=True),
        ]

        # mpl.plot(data, addplot=add_plot)

        jpg_file = format("log/%s.jpg" % (self.code))

        mpf.plot(
            df,
            **kwargs,
            style=mpfStyle,
            show_nontrading=False,
            addplot=add_plot,
            warn_too_much_data=10000,
            savefig=jpg_file
        )
        # mpf.plot(df,**kwargs,style=mpfStyle,show_nontrading=False)
        # plt.show()

        # plt.savefig(jpg_file)

        # plt.grid() #显示网格
        # ax.xaxis_date()  #设置x轴的刻度格式为常规日期格式

    def calc(self):
        prev_state = sellout
        """boll线卖出后续到boll中轨以后再考虑买入操作"""
        for i in range(len(self.df)):
            if i <= 0:
                continue
            if i > len(self.df) - 2:
                break  # 数据结束了

            v = self.df.iloc[i - 1]
            pdif = v["dif"]
            v = self.df.iloc[i]
            cclose, cdif, cdea, cmacd, cdate, cma60 = v["close"], v["dif"], v["dea"], v["macd"], v["date"], v["ma60"]
            v = self.df.iloc[i + 1]
            nclose, ndif = v["close"], v["dif"]
            """
            条件，判定买卖关键位置 所有的[buy,sellout]都是当前信号点的下一个节点
            date,price 用的是下一个节点的
            """
            if prev_state == sellout and cclose > cma60:
                if is_bogu(pdif, cdif, ndif):
                    self.trades.append(Trade(cdate, cdif, nclose, "波谷买入"))
                    prev_state = purchase
                    continue
                elif is_jincha(cdif, cdea, cmacd):
                    self.trades.append(Trade(cdate, cdif, nclose, "金叉买入"))
                    prev_state = purchase
                    continue
            elif prev_state == purchase:
                # if is_out_of_boll_upper(chigh, cupper):
                #    self.sixtyList.append(SixtyMinter(cdate, sellout, cdif, nclose))
                #    prev_state = sellout
                #    boll_sellout = True
                #    continue
                if is_bofen(pdif, cdif, ndif):
                    self.trades[-1].sellout(nclose, "波峰卖出", cdate, cdif)
                    prev_state = sellout
                    continue
                # elif cclose <= cma10 < pma10 or cclose < cma60:
                #    """当条件A：C(60m)<=MA10(60m)&MA10(60m Ti)<MA10(60m T i-1)后sell所有股票或者仓位为0；Ture 发生的时候macd>0 or macd <0;"""
                #    self.sixtyList.append(SixtyMinter(cdate, sellout, cdif, nclose))
                #    prev_state = sellout
                #    boll_sellout = False
                #    continue

    def bill_calc(self):
        all_profit = 0
        for info in self.trades:
            if info.s_price == 0.0:
                continue
            val = info.s_price - info.b_price
            count = int(100000 / info.b_price)
            if count < 100:
                self.opt = "买不起"
                return
            if val > 0:  # 赚钱
                addMoney = (val * count) - 100  # 20手续费等
                info.profit = addMoney
                all_profit += addMoney
            else:  # 亏钱
                subMoney = (val * count) - 100  # 20手续费等
                info.profit = subMoney
                all_profit += subMoney
        self.allProfit = all_profit

    def get_content(self):
        txt = ""
        for i in reversed(self.trades):
            txt += format(
                "收益:%.2f [%s,%s] [%.3f,%.3f] [%.2f,%.2f] [%s,%s]\n"
                % (
                    i.profit,
                    i.b_date,
                    i.s_date,
                    i.b_dif,
                    i.s_dif,
                    i.b_price,
                    i.s_price,
                    i.b_msg,
                    i.s_msg,
                )
            )
        return format("总收益%f\n%s" % (self.allProfit, txt))


def calc(code: str, draw: bool):
    s = StockData(code, draw)
    cent = s.get_content()
    cent_file = format("log/%s_b.txt" % (code))
    with open(cent_file, "w", encoding="utf8") as f:
        f.write(cent)


if __name__ == "__main__":

    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 界面可带中文
    plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["font.family"] = "SimHei"
    mpl.rcParams["font.size"] = 10

    if not os.path.exists("log"):
        os.mkdir("log")

    # 账号如果提示不能用，这里换一下
    jq.auth("", "")
    df = pd.read_excel("导入测试标准格式.xls", dtype=str)
    df.apply(lambda x: calc(jq.normalize_code(x["code"]), True), axis=1)
    calc(jq.normalize_code("002424"), True)
