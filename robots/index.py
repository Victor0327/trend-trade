import numpy
import talib
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
  if type in ["stock", "domestic_goods", "etf"]:
    return get_bars(symbol, period="10d", interval="15m"), symbol_title if symbol_title else symbol, type
  else:
    return get_bars(symbol, period="15d", interval="60m"), symbol_title if symbol_title else symbol, type