import akshare as ak
import numpy as np
import pandas as pd
import os
from datetime import datetime, date

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)

if __name__ == "__main__":
    # df = ak.stock_zh_a_spot()
    # print(df.iloc[-1])

    # df1 = ak.stock_zh_a_daily("sh601611", adjust="qfq", start_date="20220601", end_date="20220610")
    # df2 = ak.stock_zh_a_daily("sh601611", adjust="qfq", start_date="20220604", end_date="20220614")
    #    print(df1.head(10))
    #    print("*" * 50)
    #    print(df2.head(10))
    # df = pd.concat([df1, df2], ignore_index=True)
    # df.drop_duplicates(inplace=True, ignore_index=True)
    # print("-" * 50)
    # print(df)
    #
    # df = ak.stock_zh_a_daily("sh601611", adjust="qfq")
    # print(df.tail(5))

    # df = ak.stock_report_fund_hold_detail(symbol="510300", date="20220630")
    # print(df)

    # df  = ak.fund_portfolio_hold_em(symbol="510300",date='20220721')
    # print(df)
    # info = os.stat("data/利润.xlsx")
    # print(int(info.st_atime))
    # print(df.iloc[-2]["date"])
    # print(df.iloc[-1]["date"])
    # print(df.tail(5))

    # df = ak.stock_zh_a_minute("sh601611", period="60", adjust="qfq")
    # print(df.tail(10))

    val = -1
    val += 1
    print(val)
    # df = ak.stock_zh_ah_spot()
    # df = ak.stock_zh_a_spot_em()
    # print(df.head(10))
    pass
