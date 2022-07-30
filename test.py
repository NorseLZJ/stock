from dis import get_instructions
import akshare as ak
from matplotlib.pyplot import axis
import numpy as np
import pandas as pd
from comm import *

querter1 = "2021年1季度股票投资明细"
querter2 = "2021年2季度股票投资明细"
querter3 = "2021年3季度股票投资明细"
querter4 = "2021年4季度股票投资明细"


def replace(querter):
    if querter == querter1:
        return 1
    if querter == querter2:
        return 2
    if querter == querter3:
        return 3
    if querter == querter4:
        return 4

    return np.nan


def collect_hold_em(symbol: str, date: str):
    if symbol == '' or date == '':
        return
    df1 = ak.fund_portfolio_hold_em(symbol, date)
    df1.drop('序号', inplace=True, axis=1)
    df1['季度'] = df1.apply(lambda x: replace(x['季度']), axis=1)

    df_stock = df1[['股票代码', '股票名称']]
    # print(df_stock.head(5))
    df_stock['行业'] = df_stock.apply(lambda x: get_industry(x['股票代码']), axis=1)

    io = pd.ExcelWriter(format('%s_%s.xlsx' % (symbol, date)),
                        engine='xlsxwriter')

    df1.to_excel(io, index=False, startcol=1, startrow=3, sheet_name='all')
    df_stock.to_excel(io, startcol=1, startrow=3, sheet_name='collect')
    io.save()


if __name__ == "__main__":
    collect_hold_em('510300', '2022')
    collect_hold_em('510300', '2021')
    #collect_hold_em('510050', '2022')
    #collect_hold_em('510050', '2021')
    #collect_hold_em('510500', '2022')
    #collect_hold_em('510500', '2021')
