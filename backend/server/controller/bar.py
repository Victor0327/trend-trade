import numpy as np
import yfinance as yf

proxies = {
   'http': 'http://127.0.0.1:7890',
   'https': 'https://127.0.0.1:7890',
}

def row_to_dict(row):
  return {
      'open': row['Open'],
      'high': row['High'],
      'low': row['Low'],
      'close': row['Close'],
      'time': int(row.name.timestamp())  # 将 datetime 转换为 Unix 时间戳
  }


def get_bars(symbol, period="10d", interval="60m"):
  try:
    symbol_ticker = yf.Ticker(symbol)
    symbol_bars = symbol_ticker.history(period=period, interval=interval, proxy=proxies)

    result = symbol_bars.apply(row_to_dict, axis=1).tolist()
  except:
    print("error")
    return []


  return result
