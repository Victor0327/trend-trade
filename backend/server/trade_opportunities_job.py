import numpy
import yfinance as yf
import os
from datetime import datetime
import numpy as np
import pandas as pd
from indicator.zigzag import zigzag_indicator
from strategy.standard import is_need_to_alert
from service.postgres_engine import DBEngine
from table.trade_symbols import get_list_sql

postgres_engine = DBEngine()

def get_bars(symbol, period="10d", interval="60m"):
  symbol_ticker = yf.Ticker(symbol)
  symbol_bars = symbol_ticker.history(period=period, interval=interval)
  print(symbol_bars)
  return symbol_bars

def get_bars_by_type(symbol, type, symbol_title=None):
  try_times = 0
  if type in ["stock", "domestic_goods", "etf", "domestic_stock"]:
    # result_df = get_bars(symbol, period="15d", interval="15m")
    result_df = get_bars(symbol, period="60d", interval="60m")
  else:
    result_df = get_bars(symbol, period="15d", interval="60m")

  while result_df.empty and try_times < 5:
    result_df = get_bars(symbol, period="15d", interval="60m")
    try_times += 1

  return result_df, symbol_title if symbol_title else symbol, type


# result_df, symbol_title, type
def process_strategy(tuple):
    df, title, type = tuple
    # 计算zigzag指标，并得到极值点的位置
    extrema = zigzag_indicator(df, ext_depth=8, ext_backstep=2)

    period = 30 if type == 'domestic_stock_day' else 90
    points = 3 if type == 'domestic_stock_day' else 6
    is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema, period, points)
    if is_need is not True:
        print("no need", title)
        return False
    # 国内股票不能做空
    if (type == 'domestic_stock' or type == 'domestic_stock_day') and nearest_high_line is None:
        print("no need", title)
        return False

    print(title)

    return True


def main():
  #  get symbols array
  sql = get_list_sql({})
  trade_symbols = postgres_engine.run_sql_to_list(sql)

  for trade_symbol in trade_symbols:
     id, symbol, type, title, active_flag = trade_symbol
     process_strategy(get_bars_by_type(symbol=symbol, type=type))

main()


