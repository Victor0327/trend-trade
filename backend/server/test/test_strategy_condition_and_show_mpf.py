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

from vnpy.trader.utility import ArrayManager
from vnpy.trader.object import BarData, Exchange, Interval

import utils.mpf as mpf_utils

from indicator.zigzag import zigzag_indicator, calculate_zigzag_indicator
import strategy.standard as standard
from table.strategy_opportunities import post_sql, get_last_oppo_sql, update_breakout_high_price, update_breakout_low_price
from service.postgres_engine import post_db


def get_raw_data(startTime, endTime, pair, contractType, interval='60m'):

  api_key = 'dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB'
  secret_key = 'lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5'

  um_futures_client = UMFutures(key=api_key, secret=secret_key)



  data_list = []

  for i in range(0, 100):
    start_time = startTime + 1000 * 60 * 60 * 1500 * i
    end_time = start_time + 1000 * 60 * 60 * 1500

    if end_time > endTime:
       break

    new_data_list = um_futures_client.continuous_klines(
        pair=pair,
        contractType=contractType,
        startTime=start_time,
        endTime=end_time,
        interval=interval,
        limit=1500)

    data_list.extend(new_data_list)

  # print(data_list)


  # 只选择前5列
  selected_data = [row[:6] for row in data_list]





  # print(selected_data)
  return selected_data

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

  startTime = date_string_to_unix_ms_timestamp('2023-05-26 00:00:00')
  endTime = date_string_to_unix_ms_timestamp('2023-10-31 00:00:00')

  # 1. 读整个历史数据
  raw_data = get_raw_data(startTime, endTime, pair='BTCUSDT', contractType='PERPETUAL', interval='1h')

  # print(raw_data.__len__())

  segment_size = 90

  list_sliced_segments, df_sliced_segments, am_sliced_segments = slice_k_lines(
      symbol='BTCUSDT',
      exchange=Exchange.BINANCEFUTURES,
      interval=Interval.HOUR,
      k_lines=raw_data,
      segment_size=segment_size
     )

  # print(list_sliced_segments[0])
  # print(list_sliced_segments.__len__())




  index = 0
  for am in am_sliced_segments:
    # 先判断3根K线之前是否是盘整，再根据最后3根K线决定是否突破。
    result, real_body_max_high, real_body_min_low = standard.is_narrow_consolidation_k_bars(am, offset=-3)
    if result is True:
      breakout = standard.is_breakout_consolidation_k_lines(am, real_body_max_high, real_body_min_low)
      if breakout is None:
         df = df_sliced_segments[index]
         print('时间', df.iloc[-1])
      if breakout is not None:
        print(breakout, index)
        if index > segment_size :
          df1 = df_sliced_segments[index - segment_size]
          df2 = df_sliced_segments[index]
          df3 = df_sliced_segments[index + segment_size]
        else:
          df1 = df_sliced_segments[index]
          df2 = df_sliced_segments[index + segment_size]
          df3 = df_sliced_segments[index + segment_size * 2]


        df_combined_vertical = pd.concat([df1, df2, df3], axis=0)
        # mpf_utils.draw_k_lines(df2)
        # 创建一个addplot所需的数据结构

        # 创建水平线的数据序列
        hline_series = [np.nan] * len(df_combined_vertical)  # 用NaN初始化线段数据列表
        lline_series = [np.nan] * len(df_combined_vertical)  # 用NaN初始化线段数据列表

        hline_series[segment_size:segment_size * 2+1] = [real_body_max_high] * (segment_size + 1)  # 线段区间内设置为固定高度
        lline_series[segment_size:segment_size * 2+1] = [real_body_min_low] * (segment_size + 1)  # 线段区间内设置为固定高度



        # print(hline_series)


        apdict1 = mpf.make_addplot(hline_series, type='line', color='r', linestyle='--', width=1)
        apdict2 = mpf.make_addplot(lline_series, type='line', color='g', linestyle='--', width=1)

        mpf_utils.draw_k_lines(df_combined_vertical, addplot=[apdict1, apdict2])
        # break
    index = index + 1









# 把 raw_list 按size循环切，并转成 dataframe 、 array_manager、 原始数据
def slice_k_lines(symbol, exchange, interval, k_lines, segment_size) -> (list[list], list[pd.DataFrame], list[ArrayManager]):
    list_sliced_segments = []
    df_sliced_segments = []
    am_sliced_segments = []
    for i in range(len(k_lines) - (segment_size - 1)):  # Subtract 49 so the last iteration includes the last K-line
        list_segment = k_lines[i:i+segment_size]  # Get a segment of 50 K-lines starting from the current index
        list_sliced_segments.append(list_segment)

        # Create a DataFrame from the segment
        df_segment = pd.DataFrame(list_segment, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df_segment['date'] = pd.to_datetime(df_segment['date'], unit='ms', utc=True)
        df_segment.set_index('date', inplace=True)
        # 将索引转换为'Asia/Shanghai'时区
        df_segment.index = df_segment.index.tz_convert('Asia/Shanghai')
        df_segment['open'] = df_segment['open'].astype(float)
        df_segment['high'] = df_segment['high'].astype(float)
        df_segment['low'] = df_segment['low'].astype(float)
        df_segment['close'] = df_segment['close'].astype(float)
        df_segment['volume'] = df_segment['volume'].astype(float)
        df_sliced_segments.append(df_segment)

        # Create an ArrayManager from the segment
        am_segment = ArrayManager(size=segment_size)
        for row in list_segment:
            bar = BarData(
                symbol=symbol,
                exchange=exchange,
                datetime=row[0],
                interval=interval,
                volume=row[5],
                open_price=row[1],
                high_price=row[2],
                low_price=row[3],
                close_price=row[4],
                open_interest=0,
                gateway_name='test'
            )
            am_segment.update_bar(bar)

        am_sliced_segments.append(am_segment)

    return list_sliced_segments, df_sliced_segments, am_sliced_segments



  # draw_hl_points(df, 'test')


test_main()

# 1. 读整个历史数据
# 2. 循环遍历一段一段历史数据，直到数据符合条件
# 3. 把符合条件的数据标注，并前后多截取一部分数据，然后画图展示，判断是否符合预期。
