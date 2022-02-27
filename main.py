import requests
from datetime import datetime, time, timedelta, date
import pandas as pd
import os

START = "2021-12-01"
# Enter owners address
ADDRESS = ""


def create_directory():
    if not os.path.exists("data"):
        os.makedirs("data")


def get_all_hotspots():
    addresses = {}
    url = "https://api.helium.io/v1/accounts/" + ADDRESS + "/hotspots"
    req = requests.get(url)
    data = req.json()["data"]
    for el in data:
        addresses[el["name"]] = el["address"]
    return addresses


def get_rewards_for_day(hotspots, day):
    start = datetime.combine(day, time.min).isoformat()
    end = datetime.combine(day, time.max).isoformat()
    data_row = [day.strftime("%Y-%m-%d")]
    for hotspot in hotspots:
        url = "https://api.helium.io/v1/hotspots/" + hotspot + "/rewards/sum?min_time=" + start + "&max_time=" + end
        req = requests.get(url)
        data_row.append(req.json()["data"]["total"])
    return data_row


def get_end_of_month(day):
    next_month = day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def process_month(hotspots, dates):
    df = pd.DataFrame([], columns=["date", *hotspots.keys()])
    print("Processing month: " + dates[0].strftime("%B %Y"))
    for day in dates:
        df.loc[len(df.index)] = get_rewards_for_day(hotspots.values(), day)
    df.to_csv("data/" + dates[0].strftime("%B%Y") + ".csv", index=False)


def process_rewards():
    create_directory()
    hotspots = get_all_hotspots()
    months = pd.date_range(start=START, end=date.today(), freq='MS')
    for day in months:
        if day.month == date.today().month:
            dates = pd.date_range(day, date.today())
        else:
            dates = pd.date_range(day, get_end_of_month(day))
        process_month(hotspots, dates)


process_rewards()
