import requests
import json
from datetime import datetime
from pprint import pprint
import numpy as np

# ---------------------------------------------
# バックテスト用の設定値
# ローソク足
chart_sec = 300  # 5分足
# 1トレードの枚数
lot = 1
# 手数料やスリッページ
slippage = 0.0005
# エントリー後の何足後、ポジションクローズするか
close_condition = 0


def get_price(min, before=0, after=0):
    # ---------------------------------------------
    # 過去のデータを取得する関数
    # ---------------------------------------------
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


def get_price_from_json(path):
    # ---------------------------------------------
    # JSONから価格データを読み込む関数
    # ---------------------------------------------
    file = open(path, 'r', encoding='utf-8')
    price = json.load(file)
    return price


def print_price(data):
    # ---------------------------------------------
    # 時間・始値・終値を表示する関数
    # ---------------------------------------------
    hour = datetime.fromtimestamp(
        data["close_time"]).strftime('%Y/%m/%d %H:%M')
    open_price = str(data["open_price"])
    close_price = str(data["close_price"])
    print(f"時間:{hour} 始値: {open_price} 終値: {close_price}")


def check_candle(data, side):
    # ---------------------------------------------
    # 条件に基づいて取引の実行可否を判断する関数
    # 与えられたローソク足データに対して、注文のタイプ（買い注文 or 売り注文）が実行すべきかどうかを判断
    #
    # data: ローソク足データ（辞書型）。close_price、open_price、high_price、low_price
    # side: 注文のタイプ（"buy" or "sell"）
    # ---------------------------------------------
    try:
        # ローソク足の実体（終値と始値の差）の割合。ローソク足の全体の高さ（高値と安値の差）で割る
        realbody_rate = abs(data["close_price"] - data["open_price"]
                            ) / (data["high_price"] - data["low_price"])
        # ローソク足の値上がり率。終値を始値で割り、1を引くことで計算
        increase_rate = data["close_price"] / data["open_price"] - 1
    except ZeroDivisionError as e:
        return False

    # 買い注文（side == "buy"）の場合:
    # 終値が始値よりも低い場合、取引を実行しない（return False）
    # 値上がり率が0.0003よりも小さい場合、取引を実行しない（return False）
    # 実体の割合が0.5よりも小さい場合、取引を実行しない（return False）
    # 上記のいずれの条件も満たさない場合、取引を実行する（return True）
    if side == "buy":
        if data["close_price"] < data["open_price"]:
            return False
        elif increase_rate < 0.0003:
            return False
        elif realbody_rate < 0.5:
            return False
        else:
            return True

    # 売り注文（side == "sell"）の場合:
    # 終値が始値よりも高い場合、取引を実行しない（return False）
    # 値下がり率が-0.0003よりも大きい場合、取引を実行しない（return False）
    # 実体の割合が0.5よりも小さい場合、取引を実行しない（return False）
    # 上記のいずれの条件も満たさない場合、取引を実行する（return True）
    if side == "sell":
        if data["close_price"] > data["open_price"]:
            return False
        elif increase_rate < -0.0003:
            return False
        elif realbody_rate < 0.5:
            return False
        else:
            return True


def check_ascend(data, last_data):
    # ---------------------------------------------
    # ローソク足が連続で上昇しているかをチェックする関数
    # ---------------------------------------------
    if data["open_price"] > last_data["open_price"] and data["close_price"] > last_data["close_price"]:
        return True
    else:
        return False


def check_descend(data, last_data):
    # ---------------------------------------------
    # ローソク足が連続で下落しているかをチェックする関数
    # ---------------------------------------------
    if data["open_price"] < last_data["open_price"] and data["close_price"] < last_data["close_price"]:
        return True
    else:
        return False


def buy_signal(data, last_data, flag):
    # ---------------------------------------------
    # 買いシグナルを確認し、OKだったら注文を出す関数
    # ---------------------------------------------
    if flag["buy_signal"] == 0 and check_candle(data, "buy"):
        flag["buy_signal"] = 1
    elif flag["buy_signal"] == 1 and check_candle(data, "buy") and check_ascend(data, last_data):
        flag["buy_signal"] = 2
    elif flag["buy_signal"] == 2 and check_candle(data, "buy") and check_ascend(data, last_data):
        log = "3回連続で陽線なので" + str(data["close_price"]) + "円で買い注文を入れます"
        flag["records"]["log"].append(log)
        flag["buy_signal"] = 3

        # buy order

        flag["order"]["exist"] = True
        flag["order"]["side"] = 'BUY'
        flag["order"]["price"] = round(data["close_price"] * lot)
    else:
        flag["buy_signal"] = 0

    return flag


def sell_signal(data, last_data, flag):
    # ---------------------------------------------
    # 売りシグナルを確認し、OKだったら注文を出す関数
    # ---------------------------------------------
    if flag["sell_signal"] == 0 and check_candle(data, "sell"):
        flag["sell_signal"] = 1
    elif flag["sell_signal"] == 1 and check_candle(data, "sell") and check_descend(data, last_data):
        flag["sell_signal"] = 2
    elif flag["sell_signal"] == 2 and check_candle(data, "sell") and check_descend(data, last_data):
        log = "3回連続で陰線なので" + str(data["close_price"]) + "円で売り注文を入れます"
        flag["records"]["log"].append(log)
        flag["sell_signal"] = 3

        # sell order

        flag["order"]["exist"] = True
        flag["order"]["side"] = 'SELL'
        flag["order"]["price"] = round(data["close_price"] * lot)
    else:
        flag["sell_signal"] = 0

    return flag


def close_position(data, last_data, flag):
    # ---------------------------------------------
    # 手仕舞いのシグナルが出たら決済の成行注文を出す関数
    # ---------------------------------------------
    flag["position"]["count"] += 1

    if flag["position"]["side"] == "BUY":
        if data["close_price"] < last_data["close_price"] and flag["position"]["count"] > close_condition:
            log = "前回の終値を下回ったので" + str(data["close_price"]) + "円あたりで成行で決済します\n"
            flag["records"]["log"].append(log)

            # close order

            records(flag, data)
            flag["position"]["exist"] = False
            flag["position"]["count"] = 0

    if flag["position"]["side"] == "SELL":
        if data["close_price"] > last_data["close_price"] and flag["position"]["count"] > close_condition:
            log = "前回の終値を上回ったので" + str(data["close_price"]) + "円あたりで成行で決済します\n"
            flag["records"]["log"].append(log)

            # close order

            records(flag, data)
            flag["position"]["exist"] = False
            flag["position"]["count"] = 0

    return flag


def check_order(flag):
    """
    サーバーに出した注文が約定したかどうかチェックする関数
    注文状況を確認して通っていたら以下を実行
    一定時間で注文が通っていなければキャンセルする

    Parameters
    ----------
    flag : dict

    Returns
    -------
    flag : dict
    """
    flag["order"]["exist"] = False
    flag["order"]["count"] = 0
    flag["position"]["exist"] = True
    flag["position"]["side"] = flag["order"]["side"]
    flag["position"]["price"] = flag["order"]["price"]
    return flag


def records(flag, data):
    """
    各トレードのパフォーマンスを記録する関数

    Parameters
    ----------
    flag : dict
    data : dict

    Returns
    -------
    flag : dict
    """

    # 取引手数料の計算
    entry_price = flag["position"]["price"]
    exit_price = round(data["close_price"] * lot)
    trade_cost = round((exit_price) * slippage)

    log = "取引手数料 : " + str(trade_cost) + "円\n"
    flag["records"]["log"].append(log)
    flag["recodes"]["slippage"].append(trade_cost)

    # ポジションの利益を計算
    buy_profit = exit_price - entry_price - trade_cost
    sell_profit = entry_price - exit_price - trade_cost

    # ポジションの利益を記録
    if flag["position"]["side"] == "BUY":
        flag["records"]["buy-count"] += 1
        flag["records"]["buy-profit"].append(buy_profit)
        flag["records"]["buy-return"].append(
            round(buy_profit / entry_price * 100, 4))
        if buy_profit > 0:
            flag["records"]["buy-winning"] += 1
            log = str(buy_profit) + "円の利益です\n"
            flag["records"]["log"].append(log)
        else:
            log = str(buy_profit) + "円の損失です\n"
            flag["records"]["log"].append(log)
    if flag["position"]["side"] == "SELL":
        flag["records"]["sell-count"] += 1
        flag["records"]["sell-profit"].append(sell_profit)
        flag["records"]["sell-return"].append(
            round(sell_profit / entry_price * 100, 4))
        if sell_profit > 0:
            flag["records"]["sell-winning"] += 1
            log = str(sell_profit) + "円の利益です\n"
            flag["records"]["log"].append(log)
        else:
            log = str(sell_profit) + "円の損失です\n"
            flag["records"]["log"].append(log)

    return flag


def backtest(flag):
    """
    バックテストの結果を表示する関数

    Parameters
    ----------
    flag: dict
    """

    buy_gross_profit = np.sum(flag["records"]["buy-profit"])
    sell_gross_profit = np.sum(flag["records"]["sell-profit"])

    print("バックテストの結果")
    print("--------------------------")
    print("買いエントリの成績")
    print("--------------------------")
    print("トレード回数  :  {}回".format(flag["records"]["buy-count"]))
    print("勝率          :  {}％".format(
        round(flag["records"]["buy-winning"] / flag["records"]["buy-count"] * 100, 1)))
    print("平均リターン  :  {}％".format(
        round(np.average(flag["records"]["buy-return"]), 4)))
    print("総損益        :  {}円".format(np.sum(flag["records"]["buy-profit"])))

    print("--------------------------")
    print("売りエントリの成績")
    print("--------------------------")
    print("トレード回数  :  {}回".format(flag["records"]["sell-count"]))
    print("勝率          :  {}％".format(
        round(flag["records"]["sell-winning"] / flag["records"]["sell-count"] * 100, 1)))
    print("平均リターン  :  {}％".format(
        round(np.average(flag["records"]["sell-return"]), 4)))
    print("総損益        :  {}円".format(np.sum(flag["records"]["sell-profit"])))

    print("--------------------------")
    print("総合の成績")
    print("--------------------------")
    print("総損益        :  {}円".format(
        np.sum(flag["records"]["sell-profit"]) + np.sum(flag["records"]["buy-profit"])))
    print("手数料合計    :  {}円".format(np.sum(flag["records"]["slippage"])))

    # ログをファイルに保存
    file = open(
        "{0}-log.txt".format(datetime.now().strftime("%Y%m%d-%H%M")), "wt", encoding="utf-8")
    file.writelines(flag["records"]["log"])


def run_test():
    price = get_price(chart_sec, after=1514764800)

    print("--------------------------")
    print("バックテストを開始します")
    print("--------------------------")
    print("開始時点:" + str(price[0]["close_time_dt"]))
    print("終了時点:" + str(price[-1]["close_time_dt"]))
    print(str(len(price)) + "件のローソク足データを取得")
    print("--------------------------")

    # フラグの初期化
    last_data = price[0]

    flag = {
        "buy_signal": 0,
        "sell_signal": 0,
        "order": {
            "exist": False,
            "side": "",
            "price": 0,
            "count": 0
        },
        "position": {
            "exist": False,
            "side": "",
            "price": 0,
            "count": 0
        },
        "records": {
            "buy-count": 0,
            "buy-profit": [],
            "buy-return": [],
            "buy-winning": 0,
            "sell-count": 0,
            "sell-profit": [],
            "sell-return": [],
            "sell-winning": 0,
            "slippage": [],
            "log": []
        }
    }

    i = 1

    while i < len(price):
        if flag["order"]["exist"]:
            flag = check_order(flag)

        data = price[i]
        # flag = log_price(flag, data)

        if flag["position"]["exist"]:
            flag = close_condition(flag, data)
        else:
            flag = buy_signal(data, last_data, flag)
            flag = sell_signal(data, last_data, flag)
        last_data["close_time"] = data["close_time"]
        last_data["open_price"] = data["open_price"]
        last_data["close_price"] = data["close_price"]

    backtest(flag)


def gathering_data():
    # ---------------------------------------------
    # データを集計し、JSONにまとめる関数
    # ---------------------------------------------
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
    # gathering_data()
    run_test()
