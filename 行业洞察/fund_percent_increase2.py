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
    try:
        df = ak.fund_etf_hist_em(symbol=code, adjust="qfq")
        columns = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
        }
        df.rename(inplace=True, columns=columns)
        df = df[df["date"] > "2020-01-01"]
        maxidx = df["close"].idxmax()
        minidx_after_max = df.loc[maxidx:]["close"].idxmin()
        if maxidx > minidx_after_max:
            # 不符合要求的
            return None

        max_close = df.loc[maxidx, "close"]
        min_close_after_max = df.loc[minidx_after_max, "close"]
        last_close = df.iloc[-1]["close"]
        drop_percentage = (max_close - min_close_after_max) / max_close * 100
        rise_percentage = (last_close - min_close_after_max) / min_close_after_max * 100
        print(f"{name} {code} dw {drop_percentage:.2f}% ,up:{rise_percentage:.2f}%")
        return [code, name, np.round(drop_percentage, 2), np.round(rise_percentage, 2)]
    except Exception as e:
        return None


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
                _data = result.result()
                if _data is not None:
                    data.append(_data)
            except Exception as e:
                print(f"处理失败", e)

    df_ret = pd.DataFrame(columns=["代码", "名称", "跌幅", "涨幅"], data=data)
    df_ret = df_ret.drop_duplicates(subset="名称", ignore_index=True)
    df_ret.sort_values(by=["跌幅"], inplace=True, ignore_index=True, ascending=False)
    df_ret.to_excel(f"{daily}_所有etf基金_跌幅.xlsx", index=False)

    # df_ret.sort_values(by=["名称"], inplace=True, ignore_index=True, ascending=False)
    # df_ret.to_excel(f"{daily}_所有etf基金_涨跌幅_NAME.xlsx", index=False)

    print(f"处理结束 {daily}")


if __name__ == "__main__":
    run_task()
