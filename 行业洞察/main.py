import akshare as ak
import os
import pandas as pd

spot_df_file = "spot.xlsx"


def handle_one_spot(_symbol: str, stock_name: str):
    """
    :param _symbol:
    :param stock_name:
    :return:
    """
    stock_file: str = format("%s.xlsx" % stock_name)
    stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=_symbol)
    stock_zh_index_daily_df.to_excel(stock_file, index=False)


if __name__ == "__main__":
    if os.path.exists(spot_df_file) is False:
        stock_zh_index_spot_df = ak.stock_zh_index_spot()
        stock_zh_index_spot_df.to_excel(spot_df_file, index=False)
    stock_zh_index_spot_df = pd.read_excel(spot_df_file)
    # print(stock_zh_index_spot_df.head(5))
    stock_zh_index_spot_df.to_excel(spot_df_file, index=False)
    codes = stock_zh_index_spot_df.loc[:, ["代码", "名称"]]
    # print(codes.head(10))
    # print(codes[1, :])
    index_list = codes.index.to_list()
    # print(index_list)
    for i in index_list:
        code, name = (codes.loc[i, ["代码", "名称"]])
        handle_one_spot(code, name)
        break
