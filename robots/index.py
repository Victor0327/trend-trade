import numpy
import yfinance as yf
# from zigzag import calculate_zigzag

# cryptos
"BTC-USD"
"XRP-USD"

# goods
"GC=F"

# stock index future
"ES=F"
"YM=F"

# etf
"FAZ"

# domestic_goods
""

# currency
""

def get_bars(symbol, period="10d", interval="60m"):
  symbol_ticker = yf.Ticker(symbol)
  symbol_bars = symbol_ticker.history(period=period, interval=interval)
  print(symbol_bars)
  return symbol_bars


def get_bars_by_type(symbol, type, symbol_title=None):
  try_times = 0
  if type in ["stock", "domestic_goods", "etf", "domestic_stock"]:
    # result_df = get_bars(symbol, period="15d", interval="15m")
    result_df = get_bars(symbol, period="15d", interval="60m")
  else:
    result_df = get_bars(symbol, period="15d", interval="60m")

  while result_df.empty and try_times < 5:
    result_df = get_bars(symbol, period="15d", interval="60m")
    try_times += 1

  return result_df, symbol_title if symbol_title else symbol, type


