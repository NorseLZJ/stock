import pandas as pd
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import akshare as ak
import os
import numpy as np
import talib as tl
import redis
import time

r = redis.Redis(host="127.0.0.1", port=6379)


@csrf_exempt
def stock(req):
    if req.method == "GET":
        return render(req, "index2.html")
    result = {
        "data": "",
        "result": False,
    }
    symbol = req.POST.get("ID")
    if symbol is None or symbol == "" or len(symbol) < 6:
        return JsonResponse(result)
    symbol = format_stock(symbol)
    resp = r.exists(symbol)
    if resp != 0:
        val = r.get(symbol).decode()
        return JsonResponse({"data": val, "result": True})

    _df = get_data(symbol=symbol)
    if _df is None:
        return HttpResponse("内部错误")
    __calc_buy_sell(_df)
    data = []
    _df.drop(inplace=True, columns=["ma5", "ma10", "ma20", "ma60", "dif", "dea", "macd", "volume"])

    _df[["open", "close", "high", "low", "buy", "sell", "profit"]] = np.round(
        _df[["open", "close", "high", "low", "buy", "sell", "profit"]].astype(float), 2
    )

    _df.reset_index().apply(
        lambda x: data.append(
            [
                str(x["date"]).replace("-", "/"),
                str(x["open"]),
                str(x["close"]),
                str(x["low"]),
                str(x["high"]),
                str(x["buy"]),
                str(x["sell"]),
                str(x["profit"]),
            ]
        ),
        axis=1,
    )

    r.setex(symbol, 60 * 60, str(data))

    val = {
        "data": str(data),
        "result": True,
    }
    return JsonResponse(val)


def index(request):
    return render(request, "index.html")


def index2(request):
    return render(request, "layout.html")


if __name__ == "__main__":
    df = get_data("sz000001")
    __calc_buy_sell(df)
    df.to_excel("temp.xlsx")
    """
    df.reset_index().apply(
        lambda x: val.append(
            [
                str(x["day"]).replace("-", "/"),
                str(np.round(x["open"], 2)),
                str(np.round(x["close"], 2)),
                str(np.round(x["low"], 2)),
                str(np.round(x["high"], 2)),
                str(x["buy"]),
                str(x["sell"]),
            ]
        ),
        axis=1,
    )
    df.drop(inplace=True, columns=['ma5', 'ma10', 'ma20', 'ma60', 'dif', 'dea', 'macd', 'volume'])
    df[['open', 'close', 'high', 'low', 'buy', 'sell']] = np.round(
        df[['open', 'close', 'high', 'low', 'buy', 'sell']].astype(float), 2)
    df.to_csv("test.csv")
    """
