"""
利润表相关的处理
"""

import pandas as pd


def CleanLRB(df: pd.DataFrame) -> pd.DataFrame:
    """
    统一的利润表处理
    """
    df = df.loc[
        (df["净利润同比"] > 5.0)
        & (df["净利润同比"] < 300.0)
        & (df["股票简称"].str.find("ST") == -1)
        & (df["股票简称"].str.find("退") == -1),
        :,
    ]
    return df


def DelLRBColumn(df: pd.DataFrame):
    """
    数据处理完之后这些就可以删除了
    """
    df.drop(
        inplace=True,
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
            # "公告日期",
            # "industry",
            # "signle",
            "序号",
        ],
    )
