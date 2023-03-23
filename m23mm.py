import ccxt
from pprint import pprint
from settings import API_KEY, API_SECRET

bitflyer = ccxt.bitflyer({
  "api_key": API_KEY,
  "secret": API_SECRET
})

# 通貨
symbol = "BTC/JPY"

def get_market():
# ----------------------------------------------
# 取引所の通貨情報を取得。例：
# 'BTC/JPY': {'active': True,
            #  'base': 'BTC',
            #  'baseId': 'BTC',
            #  'contract': False,
            #  'contractSize': None,
            #  'expiry': None,
            #  'expiryDatetime': None,
            #  'future': False,
            #  'id': 'BTC_JPY',
            #  'info': {'market_type': 'Spot', 'product_code': 'BTC_JPY'},
            #  'inverse': None,
            #  'limits': {'amount': {'max': None, 'min': None},
            #             'cost': {'max': None, 'min': None},
            #             'leverage': {'max': None, 'min': None},
            #             'price': {'max': None, 'min': None}},
            #  'linear': None,
            #  'maker': 0.002,
            #  'margin': False,
            #  'option': False,
            #  'optionType': None,
            #  'percentage': True,
            #  'precision': {'amount': None, 'price': None},
            #  'quote': 'JPY',
            #  'quoteId': 'JPY',
            #  'settle': None,
            #  'settleId': None,
            #  'spot': True,
            #  'strike': None,
            #  'swap': False,
            #  'symbol': 'BTC/JPY',
            #  'taker': 0.002,
            #  'type': 'spot'},
  markets = bitflyer.load_markets()
  pprint(markets)

# ------------------------------------------------------------
# 取引所の板情報を取得
#  'ask': 3649058.0,
#  'askVolume': None,
#  'average': None,
#  'baseVolume': 3499.57269325,
#  'bid': 3647991.0,
#  'bidVolume': None,
#  'change': None,
#  'close': 3648140.0,
#  'datetime': '2023-03-23T08:31:22.247Z',
#  'high': None,
#  'info': {'best_ask': '3649058.0',
#           'best_ask_size': '0.02',
#           'best_bid': '3647991.0',
#           'best_bid_size': '0.00911',
#           'ltp': '3648140.0',
#           'market_ask_size': '0.0',
#           'market_bid_size': '0.0',
#           'product_code': 'BTC_JPY',
#           'state': 'RUNNING',
#           'tick_id': '7534812',
#           'timestamp': '2023-03-23T08:31:22.247',
#           'total_ask_depth': '309.12035872',
#           'total_bid_depth': '498.59724936',
#           'volume': '14089.71756056',
#           'volume_by_product': '3499.57269325'},
#  'last': 3648140.0,
#  'low': None,
#  'open': None,
#  'percentage': None,
#  'previousClose': None,
#  'quoteVolume': None,
#  'symbol': 'BTC/JPY',
#  'timestamp': 1679560282247,
#  'vwap': None}
def fetch_ticker(symbol):
  ticker = bitflyer.fetch_ticker(symbol)
  pprint(ticker)

# ---------------------------------------------
# 板情報を注文量と合わせて取得
#           .....
#           [1568800.0, 3.0],
#           [1561350.0, 0.001],
#           [1551000.0, 0.06],
#           [1550000.0, 0.517],
#           [1535000.0, 0.1],
#           [1530000.0, 0.1],
#           [1528000.0, 0.1],
#           [1524650.0, 0.003],
#           [1519400.0, 0.001],
#           [1506300.0, 0.006],
#           [1500000.0, 3.15933866],
#           [1420000.0, 0.5],
#           [1400000.0, 0.084],
#           [1399000.0, 0.00104999],
#           [1380000.0, 1.4655],
#           [1375000.0, 1.0],
#           [1370000.0, 1.0],
#           [61895.0, 0.00849]],
#  'datetime': None,
#  'nonce': None,
#  'symbol': 'BTC/JPY',
#  'timestamp': None}
def fetch_order_book(symbol="BTC/JPY"):
  order_book = bitflyer.fetch_order_book(symbol)
  pprint(order_book)


# ---------------------------------------------
# ローソク足情報の取得
# [[1679560440000,
#   3645618.0,
#   3645618.0,
#   3644354.0,
#   3644354.0,
#   0.14823398000000002],
#  [1679560500000,
#   3644354.0,
#   3644651.0,
#   3642795.0,
#   3643440.0,
#   1.4045539000000002],
#  [1679560560000, 3643440.0, 3643440.0, 3643438.0, 3643438.0, 0.04230954]]
def fetch_candles(timeframe='1m', symbol='BTC/JPY'):
  candles = bitflyer.fetch_ohlcv(symbol, timeframe, since=None, limit=None, params={})
  pprint(candles)


# ---------------------------------------------
# 口座残高の取得
# {'BAT': {'free': 9.67671646, 'total': 9.67671646, 'used': 0.0},
#  'BCH': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  'BTC': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  'DOT': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  'ETC': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  'ETH': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  'FLR': {'free': 0.0, 'total': 0.0, 'used': 0.0},
#  ....
def fetch_account_balance():
  balance = bitflyer.fetch_balance()
  pprint(balance)

def create_order(price, side, amount, symbol="BTC/JPY"):
  order = bitflyer.create_order(
    symbol,
    type='limit',
    price=price,
    side=side,
    amount=amount,
  )
  pprint(order)

if __name__ == "__main__":
  # get_market()
  # fetch_ticker(symbol)
  # fetch_order_book(symbol)
  # fetch_candles()
  fetch_account_balance()
  # create_order(price=4000000, side="buy", amount=0.001)