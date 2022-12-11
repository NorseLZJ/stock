import akshare as ak
import os
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)

if __name__ == "__main__":
    if os.path.exists("covid.xlsx") is False:
        covid_19_risk_area_df = ak.covid_19_risk_area(symbol="高风险等级地区")
        covid_19_risk_area_df.to_excel("covid.xlsx", index=False)
    covid_df = pd.read_excel("covid.xlsx")
    df = covid_df[(covid_df["city"] == "西安市") & (covid_df["county"] == "未央区")]
    print(df)
    print(df.loc[:, ["communitys"]])
