import sys
import os
import numpy as np
import yfinance as yf

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))

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
    symbol_bars = symbol_ticker.history(period=period, interval=interval)

    result = symbol_bars.apply(row_to_dict, axis=1).tolist()
    print(result)
  except:
    print("error")
    return []


  return result


get_bars('AAPL')