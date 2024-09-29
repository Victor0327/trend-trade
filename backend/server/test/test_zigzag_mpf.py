from itertools import combinations
import time
import os
from datetime import datetime
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))
from binance.um_futures import UMFutures

from utils.date import date_string_to_unix_ms_timestamp, unix_ms_timestamp_to_date_string, get_current_date, get_delta_date
from utils.math import calculate_atr

from indicator.zigzag import zigzag_indicator, calculate_zigzag_indicator
from strategy.standard import is_need_to_alert
from table.strategy_opportunities import post_sql, get_last_oppo_sql, update_breakout_high_price, update_breakout_low_price
from service.postgres_engine import post_db


def get_df(startTime, endTime, pair, contractType, interval='60m'):

  api_key = 'dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB'
  secret_key = 'lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5'

  um_futures_client = UMFutures(key=api_key, secret=secret_key)

  # 一次读取90根K线进行判断。如果是15分钟的话，就是一天的数据

  data_list = um_futures_client.continuous_klines(
      pair=pair,
      contractType=contractType,
      startTime=startTime,
      endTime=endTime,
      interval=interval,
      limit=300)

  # 只选择前5列
  selected_data = [row[:5] for row in data_list]

  df = pd.DataFrame(selected_data, columns=['date', 'open', 'high', 'low', 'close'])
  df['open'] = df['open'].astype(float)
  df['high'] = df['high'].astype(float)
  df['low'] = df['low'].astype(float)
  df['close'] = df['close'].astype(float)
  df['date'] = pd.to_datetime(df['date'], unit='ms').astype(str)
  # df['date'] = pd.to_datetime(df['date'])  # 将'date'列转换为 datetime 类型
  df.set_index('date', inplace=True)       # 设置'date'列为索引
  # 确保df的索引是日期时间数据
  df.index = pd.to_datetime(df.index)



  print(df)
  return df

def draw_hl_points(df, title):
    print(df.__len__())
    # 计算zigzag指标，并得到极值点的位置
    high_list = df['high'].tolist()
    low_list = df['low'].tolist()
    date_list = df.index.tolist()

    # atr = calculate_atr(df, period=200)
    # print(atr.iloc[-1])

    extrema = calculate_zigzag_indicator(high_list=high_list, low_list=low_list, depth=7, deviation=0, backstep=3)
    # extrema = zigzag_indicator(df=df)
    print(extrema)

    # period = 90
    # points = 6
    # is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema, period, points)
    # if is_need is not True:
    #     print("no need", title)
    #     return False

    # 高点和低点的index和price
    high_points = [(point['index'], point['price']) for point in extrema if point['type'] == 'high']
    low_points = [(point['index'], point['price']) for point in extrema if point['type'] == 'low']

    # 高点和低点的index
    high_indexes = [idx for idx, price in high_points]
    low_indexes = [idx for idx, price in low_points]

    # 高点和低点的价格
    high_prices = [price for idx, price in high_points]
    low_prices = [price for idx, price in low_points]

    # 使用df的索引创建一个新的pandas Series，并使用NaN填充
    high_prices_series = pd.Series(np.full(len(df), np.nan), index=df.index)
    low_prices_series = pd.Series(np.full(len(df), np.nan), index=df.index)

    # 更新高点和低点的价格
    high_prices_series.loc[df.index[high_indexes]] = high_prices
    low_prices_series.loc[df.index[low_indexes]] = low_prices

    # 使用新创建的Series创建addplot对象
    apds = [mpf.make_addplot(high_prices_series, scatter=True, type='line', color='r', linewidths=1.5, marker='o', markersize=10),
            mpf.make_addplot(low_prices_series, scatter=True, type='line', color='g', linewidths=1.5, marker='o', markersize=10)]

    mpf.plot(df, type='candle', addplot=apds, style='starsandstripes', title=title)

    # if nearest_high_line is not None:
    #     apds.append(mpf.make_addplot([nearest_high_line] * len(df), scatter=True,  type='line', color='r'))

    # if nearest_low_line is not None:
    #     apds.append(mpf.make_addplot([nearest_low_line] * len(df), scatter=True,  type='line', color='g'))

    # if nearest_high_line or nearest_low_line:
    #     print("need", title)
    #     mpf.plot(df, type='candle', addplot=apds, style='starsandstripes', title=title)
        # 画图

def test_main():
  symbol = 'BTCUSDT_PERPETUAL'

  startTime = date_string_to_unix_ms_timestamp('2023-08-26 00:00:00')
  endTime = date_string_to_unix_ms_timestamp('2023-10-15 00:00:00')

  df = get_df(startTime, endTime, pair='BTCUSDT', contractType='PERPETUAL', interval='1h')
  draw_hl_points(df, 'test')

def is_difference_less_than_threshold(prices, threshold) -> (list, list):
        lines = []
        # index price type
        points = []
        for combo in combinations(prices, 3):
            price_values = [x['price'] for x in combo]
            max_price = max(price_values)
            min_price = min(price_values)
            avg_price = sum(price_values) / 3
            diff = max_price - min_price

            # 如果3个价格之间的最大差异小于阈值，则返回True
            if diff < threshold:
                lines.append(avg_price)
                points.append(combo)

        return lines, points

def test_is_difference_less_than_threshold():
    highs = [{'index': 7, 'price': 27308.7, 'type': 'high'}, {'index': 22, 'price': 27231.5, 'type': 'high'}, {'index': 50, 'price': 26987.6, 'type': 'high'}, {'index': 54, 'price': 27085.0, 'type': 'high'}, {'index': 73, 'price': 27279.5, 'type': 'high'}, {'index': 101, 'price': 28613.0, 'type': 'high'}, {'index': 117, 'price': 27665.0, 'type': 'high'}, {'index': 145, 'price': 27627.6, 'type': 'high'}, {'index': 159, 'price': 27890.0, 'type': 'high'}, {'index': 173, 'price': 28110.0, 'type': 'high'}, {'index': 193, 'price': 27785.0, 'type': 'high'}, {'index': 198, 'price': 28035.6, 'type': 'high'}]
    lows = [{'index': 17, 'price': 26850.0, 'type': 'low'}, {'index': 29, 'price': 26625.0, 'type': 'low'}, {'index': 52, 'price': 26890.4, 'type': 'low'}, {'index': 60, 'price': 26929.8, 'type': 'low'}, {'index': 83, 'price': 27015.0, 'type': 'low'}, {'index': 108, 'price': 27255.0, 'type': 'low'}, {'index': 131, 'price': 27123.0, 'type': 'low'}, {'index': 149, 'price': 27317.1, 'type': 'low'}, {'index': 166, 'price': 27533.1, 'type': 'low'}, {'index': 176, 'price': 27333.5, 'type': 'low'}, {'index': 196, 'price': 27156.0, 'type': 'low'}]
    high_lines, key_high_points = is_difference_less_than_threshold(highs[-12:], threshold = 100)
    low_lines, key_low_points = is_difference_less_than_threshold(lows[-12:], threshold = 100)
    print(high_lines, low_lines)



test_main()

# test_is_difference_less_than_threshold()