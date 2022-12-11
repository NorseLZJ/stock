import akshare as ak
import os
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)

covid_csv = "covid.csv"

if __name__ == "__main__":
    if os.path.exists(covid_csv) is False:
        covid_19_risk_area_df = ak.covid_19_risk_area(symbol="高风险等级地区")
        covid_19_risk_area_df.to_csv(covid_csv, index=False)
    covid_df = pd.read_csv(covid_csv)
    df_xa = covid_df[(covid_df["city"] == "西安市")]
    df = covid_df[(covid_df["city"] == "西安市") & (covid_df["county"] == "未央区")]
    print("西安高风险数量:", len(df_xa))
    print(df.loc[:, ["communitys"]].to_string(index=False))
    # print(df.to_string(index=False))
