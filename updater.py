import twitter
import pandas as pd
import datetime as dt

schedule = pd.read_csv("schedule.csv")
for i, row in schedule.iterrows():
    if row["sent"] == False:
        while dt.datetime.strptime(row["datetime"], '%Y-%m-%d %H:%M:%S') > dt.datetime.now(): pass
        twitter.tweet(row["msg"], row["img"])
        row["sent"] = True
        schedule.iloc[i] = row
