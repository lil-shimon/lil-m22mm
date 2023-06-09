import ccxt
import datetime
import time
import json

# TODO:
# 1. o 現在の価格を取得
# 2. シンプルなマーケットメイキング戦略の実装: 現行市場価格から0.5%引いた価格で買い注文を、現行市場価格に0.5%加えた価格で売り注文
# 3. 注文の監視と調整: オーダーブックを継続的に監視し、市場価格の変動に応じて注文を調整。現在の市場価格から離れすぎた注文は、キャンセルして置き換え
# 4. 注文サイズを調整: 利用可能な資本の小さな割合、1%。
# 5. 動的スプレッドの使用: スプレッドを市場の状況に応じて調整することで（例えば、高いボラティリティの期間中はスプレッドを広げ、低いボラティリティの期間中は縮める）、注文の約定確率を向上。
# 6. リスク管理戦略の実装: 一度にリスクを負う資本の最大割合を設定することで、リスクを制限。また、市場が自分のポジションに逆行した場合の損失を最小限に抑えるため、逆指値注文（ストップロス）を使用。
# 7. 複数通貨ペアのサポート: MMBOTを複数の通貨ペアで動作させ、利益機会を最大化する。ただし、リスクを適切に管理するため、各通貨ペアに対する資本の割り当てを適切に調整する
# 8. ボットのバックテスト: MMBOTの戦略を過去の市場データでバックテストし、パフォーマンスやリスクを評価。戦略の改善やリスク管理の最適化
# 9. リアルタイムのパフォーマンスモニタリング: MMBOTのパフォーマンスをリアルタイムで監視し、異常が検出された場合にアラートを送信する仕組みを導入。-> リスクの早期察知やトラブルシューティング
# 10. APIレート制限の管理: 取引所APIのレート制限に対処するため、リクエストの頻度を調整し、API制限に達した場合に適切な待機時間を設定
# 11. フォールバック戦略: 取引所のAPI接続に問題が発生した場合や、価格データが取得できない場合に、フォールバック戦略を実装して、ボットが安全に停止または継続することができるように

# 取引ペア
symbol = "BTC/JPY"

api_key = "todo"
api_secret = "todo"

# BitFlyerのAPIにアクセスするために必要な認証情報が設定
exchange = ccxt.bitflyer({
  api_key: api_key,
  api_secret: api_secret
})

# 時刻系
date_format = "%Y年%m月%d日 %H時%M分%S秒"

# 最新の価格情報を取得する
def get_ticker():
    # 取得した価格情報が格納
    ticker = exchange.fetch_ticker(symbol)
    # 取得した価格情報から、最新の価格を取り出して格納
    last_price = ticker["last"]
    return last_price

def place_orders():
   try:
    current_price = get_ticker()

    # 買い注文と売り注文の価格を計算
    bid_price = current_price * 0.995
    ask_price = current_price * 1.005

    # 注文量を指定
    order_amount = 0.001

    # 買い注文を出す
    bid_order = exchange.create_limit_buy_order(symbol, order_amount, bid_price)
    print(f"Buy order placed at {buy_price}")

    # 売り注文を出す
    ask_order = exchange.create_limit_sell_order(symbol, order_amount, ask_price)
    print(f"Sell order placed at {ask_price}")
   except Exception as e:
    print("f:Error occurred: {e}")


# 過去のデータを取得
def fetch_historical_data():
  timeframe = "1h"
  since = exchange.parse8601('2022-01-01T00:00:00Z')
  now = exchange.milliseconds()

  all_candles = []
  while since < now:
    candles = exchange.fetch_ohlcv(symbol, timeframe, since)
    if len(candles)==0:
      break
    since = candles[-1][0]+1
    print(f"since: {since} candles: {candles}")
    all_candles += candles

  file = open("./{0}-{1}-price.json".format(since, now))
  json.dump(all_candles, file)
  return all_candles

def back_test(data):
  print(f"data: {data}")
  # 開始時のバランス
  balance = 100000
  order_amount = 0.001

  for i in range(len(data)-1):
    current_price = data[i][4] # 終値
    next_open_price = data[i+1][1] #次の始値
    print(f"current_price: {current_price}, next_open_price: {next_open_price}")

    bid_price = current_price * 0.995
    ask_price = current_price * 1.005

    print(f"bid: {bid_price}, next_open_price: {next_open_price}, next_open_price <= bid_price: {next_open_price<=bid_price}")

    if next_open_price <= bid_price:
      balance -= order_amount * bid_price
      balance += order_amount * ask_price

    # buy_price = current_price * 1.005
    # sell_price = current_price * 0.995

    # if buy_price <= next_open_price <= sell_price:
    #   balance -= order_amount * buy_price
    #   balance += order_amount * sell_price

  return balance

def test():
  historical_data = fetch_historical_data()
  initial_balance = 100000
  final_balance = back_test(historical_data)
  profit = final_balance - initial_balance
  print(f"Initial balance: {initial_balance}")
  print(f"Final balance: {final_balance}")
  print(f"Profit: {profit}")

def fetch_realtime_data():
  while True:
    last_price = get_ticker()
    now = datetime.datetime.now()
    print(f"Bitflyer {symbol}: ", last_price, f"{now.strftime(date_format)}")
    time.sleep(3)
  

def main():
  test()

if __name__ == "__main__":
    main()