import ccxt
import datetime

# TODO:
# 1. o 現在の価格を取得
# 2. シンプルなマーケットメイキング戦略の実装: 現行市場価格から0.5%引いた価格で買い注文を、現行市場価格に0.5%加えた価格で売り注文
# 3. 注文の監視と調整: オーダーブックを継続的に監視し、市場価格の変動に応じて注文を調整。現在の市場価格から離れすぎた注文は、キャンセルして置き換え
# 4. 注文サイズを調整: 利用可能な資本の小さな割合、1%。
# 5. 動的スプレッドの使用: スプレッドを市場の状況に応じて調整することで（例えば、高いボラティリティの期間中はスプレッドを広げ、低いボラティリティの期間中は縮める）、注文の約定確率を向上。
# 6. リスク管理戦略の実装: 一度にリスクを負う資本の最大割合を設定することで、リスクを制限。また、市場が自分のポジションに逆行した場合の損失を最小限に抑えるため、逆指値注文（ストップロス）を使用。

# 取引ペア
symbol = "BTC/JPY"

# BitFlyerのAPIにアクセスするために必要な認証情報が設定
exchange = ccxt.bitflyer()

# 時刻系
date_format = "%Y年%m月%d日 %H時%M分%S秒"

# 最新の価格情報を取得する
def get_ticker():
    # 取得した価格情報が格納
    ticker = exchange.fetch_ticker(symbol)
    # 取得した価格情報から、最新の価格を取り出して格納
    last_price = ticker["last"]
    return last_price

def main():
  while True:
    last_price = get_ticker()
    now = datetime.datetime.now()
    print(f"Bitflyer {symbol}: ", last_price, f"{now.strftime(date_format)}")

if __name__ == "__main__":
    main()