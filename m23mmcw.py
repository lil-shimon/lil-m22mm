import requests
import json
from datetime import datetime
from pprint import pprint


def get_price(min, before=0, after=0):
    price = []
    params = {"period": min}
    if before != 0:
        params["before"] = before
    if after != 0:
        params["after"] = after

    response = requests.get(
        "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params)
    data = response.json()
    # pprint(data)

    if data["result"][str(min)] is not None:
        for i in data["result"][str(min)]:
            price.append({"close_time": i[0], "close_time_dt": datetime.fromtimestamp(
                i[0]).strftime('%Y/%m/%d %H:%M'), "open_price": i[1], "high_price": i[2], "low_price": i[3], "close_price": i[4]})
        return price
    else:
        print("there is no data")
        return None


def gathering_data():
    price = get_price(60)
    print("先頭データ : " + price[0]["close_time_dt"] +
          "  UNIX時間 : " + str(price[0]["close_time"]))
    print("末尾データ : " + price[-1]["close_time_dt"] +
          "  UNIX時間 : " + str(price[-1]["close_time"]))
    print("合計 ： " + str(len(price)) + "件のローソク足データを取得")
    print("--------------------------")
    print("--------------------------")
    file = open("./{0}-{1}-price.json".format(
        price[0]["close_time"], price[-1]["close_time"]), "w", encoding="utf-8")
    json.dump(price, file, indent=4)


if __name__ == "__main__":
    gathering_data()
