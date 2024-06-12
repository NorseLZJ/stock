import akshare as ak
import os
import pandas as pd
import numpy as np
import time
import concurrent.futures
import multiprocessing


def GET_MAX_THREADS():
    return int(multiprocessing.cpu_count() * 0.6)


def task(code: str, name: str):
    columns = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
    }
    try:
        df = ak.fund_etf_hist_em(symbol=code, adjust="qfq")
        df.rename(inplace=True, columns=columns)
        df = df[df["date"] > "2024-01-01"]
        idx_min = df["close"].idxmin()
        df = df[df["date"] > df.loc[idx_min]["date"]]
        df.reset_index(drop=True, inplace=True)
        if df["close"].idxmin() < df["close"].idxmax():
            max_value = df["close"].max()
            min_value = df["close"].min()
            sub_value = (max_value - min_value) / min_value * 100
            return code, name, np.round(sub_value, 2)
        else:
            return None
    except Exception as e:
        return None


def create_dir(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def run_task():
    etf = ak.fund_etf_category_sina(symbol="ETF基金")
    data = []
    daily = time.strftime("%Y-%m-%d", time.localtime(time.time()))

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=GET_MAX_THREADS()
    ) as executor:
        results = []
        for idx in range(len(etf)):
            (code, name) = etf.iloc[idx][["代码", "名称"]]
            code = str(code).replace("sz", "", -1).replace("sh", "", -1)
            results.append(executor.submit(task, code, name))

        for result in concurrent.futures.as_completed(results):
            try:
                (code, name, vv) = result.result()
                print(f"处理成功 {code} --- {vv}")
                data.append([code, name, vv])
            except Exception as e:
                print(f"处理失败{code}", e)

    df_ret = pd.DataFrame(columns=["代码", "名称", "涨跌幅"], data=data)
    df_ret = df_ret.drop_duplicates(subset="名称", ignore_index=True)
    df_ret.sort_values(by=["涨跌幅"], inplace=True, ignore_index=True, ascending=False)
    df_ret.to_excel(f"{daily}_所有etf基金_涨跌幅.xlsx", index=False)

    df_ret.sort_values(by=["名称"], inplace=True, ignore_index=True, ascending=False)
    df_ret.to_excel(f"{daily}_所有etf基金_涨跌幅_NAME.xlsx", index=False)

    print(f"处理结束 {daily}")


if __name__ == "__main__":
    run_task()
