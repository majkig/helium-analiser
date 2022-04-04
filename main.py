import requests
from datetime import datetime, time, timedelta, date
import pandas as pd
import os
from tqdm import tqdm

import constants

START = "2021-12-01"
# Enter owners address
ADDRESS = constants.WALLET_ADDRESS


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


def check_address():
    if len(ADDRESS) == 0 or ADDRESS.isspace():
        print("Empty address entered")
        exit()
    url = "https://api.helium.io/v1/accounts/" + ADDRESS
    req = requests.get(url)
    if not req.json()["data"].get("hotspot_count"):
        print("Invalid address entered")
        exit()


def check_month(hotspots, dates):
    file_path = "data/" + dates[0].strftime("%B%Y") + ".csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep=';', decimal=',')
        return df.keys().size == len(hotspots) + 1 and len(dates) == len(df)
    return False


def process_month(hotspots, dates):
    df = pd.DataFrame([], columns=["date", *hotspots.keys()])
    print("Processing month: " + dates[0].strftime("%B %Y"))
    for day in tqdm(dates):
        df.loc[len(df.index)] = get_rewards_for_day(hotspots.values(), day)
    df.to_csv("data/" + dates[0].strftime("%B%Y") + ".csv", index=False, sep=';', decimal=',')


def process_rewards():
    check_address()
    create_directory()
    hotspots = get_all_hotspots()
    months = pd.date_range(start=START, end=date.today(), freq='MS')
    for day in months:
        if day.month == date.today().month:
            dates = pd.date_range(day, date.today())
        else:
            dates = pd.date_range(day, get_end_of_month(day))
        if check_month(hotspots, dates):
            print(dates[0].strftime("%B %Y") + " already processed")
        else:
            process_month(hotspots, dates)


process_rewards()
