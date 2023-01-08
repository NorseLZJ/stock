import pandas as pd
from akshare import *
import os


if __name__ == "__main__":
    # df = pd.DataFrame(data={"code": ["001", "002", "003"]})
    # df.astype({"code": "object"}).dtypes
    # df.to_csv("temp.csv", index=False)

    # df = stock_lrb_em()
    df = pd.read_csv("temp.csv")
    df.astype({"股票代码": "str"}).dtypes
    df.drop(
        columns=[
            "净利润",
            "净利润同比",
            "营业总收入",
            "营业总收入同比",
            "营业总支出-营业支出",
            "营业总支出-销售费用",
            "营业总支出-管理费用",
            "营业总支出-财务费用",
            "营业总支出-营业总支出",
            "营业利润",
            "利润总额",
        ],
        inplace=True,
    )
    df.to_csv("temp.csv")
    pass
    """
    x = "净利润,净利润同比,营业总收入,营业总收入同比,营业总支出-营业支出,营业总支出-销售费用,营业总支出-管理费用,营业总支出-财务费用,营业总支出-营业总支出,营业利润,利润总额,公告日期,industry,signle"
    ss = x.split(",")
    v = "["
    for i in ss:
        v += format('"%s",' % (i))
    v += "]"
    print(v)
    """
    """
    files = os.listdir("out")
    for file in files:
        ss = file.split(".")
        if ss[1] == "xlsx":
            df = pd.read_excel(format("out/%s" % (file)), dtype=str)
            print(df.head())
            df.to_csv(format("out/%s.csv" % (ss[0])), index=False)
    """
