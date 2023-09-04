import numpy as np
import yfinance as yf

def row_to_dict(row):
  return {
      'open': row['Open'],
      'high': row['High'],
      'low': row['Low'],
      'close': row['Close'],
      'time': int(row.name.timestamp())  # 将 datetime 转换为 Unix 时间戳
  }


def get_bars(symbol, period="10d", interval="60m"):
  symbol_ticker = yf.Ticker(symbol)
  symbol_bars = symbol_ticker.history(period=period, interval=interval)

  result = symbol_bars.apply(row_to_dict, axis=1).tolist()
  print(result)

  return result