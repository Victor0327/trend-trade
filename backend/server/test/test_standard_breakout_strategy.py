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

from indicator.zigzag import zigzag_indicator
from strategy.standard import is_need_to_alert
from table.strategy_opportunities import post_sql, get_last_oppo_sql, update_breakout_high_price, update_breakout_low_price
from service.postgres_engine import post_db
from service.email import send_email


def get_df(startTime, endTime, pair, contractType, interval='15m'):

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
    # 计算zigzag指标，并得到极值点的位置
    extrema = zigzag_indicator(df, ext_depth=8, ext_backstep=2)

    period = 90
    points = 6
    is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema, period, points)
    if is_need is not True:
        print("no need", title)
        return False

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

    if nearest_high_line is not None:
        apds.append(mpf.make_addplot([nearest_high_line] * len(df), scatter=True,  type='line', color='r'))

    if nearest_low_line is not None:
        apds.append(mpf.make_addplot([nearest_low_line] * len(df), scatter=True,  type='line', color='g'))

    if nearest_high_line or nearest_low_line:
        print("need", title)
        mpf.plot(df, type='candle', addplot=apds, style='starsandstripes', title=title)
        # 画图


symbol = 'BTCUSDT_PERPETUAL'
for i in range(700, 0 , -1):
  i = i - 1
  from_minutes = i * 15
  to_minutes = from_minutes - 300 * 15

  startTime = date_string_to_unix_ms_timestamp(get_delta_date(format='%Y-%m-%d %H:%M:%S', minutes=from_minutes), timezone='Asia/Shanghai')
  endTime = date_string_to_unix_ms_timestamp(get_delta_date(format='%Y-%m-%d %H:%M:%S', minutes=to_minutes), timezone='Asia/Shanghai')
  print(from_minutes, to_minutes)

  df = get_df(startTime, endTime, pair='BTCUSDT', contractType='PERPETUAL', interval='15m')
  print(df.iloc[-1])
  print(df.index[-1])

  extrema = zigzag_indicator(df, ext_depth=8, ext_backstep=2)
  period = 90
  points = 6
  is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema, period, points)

  # 取上一次策略、当前是否是机会、当前的高低收盘价。


  # 1. 如果没创建过数据，且产生新的机会，则报警，记录机会。
  # 2. 上次策略没被穿过，比较当前的阻力和支持是否和上次的一样，如果一样，则什么都不做，如果不一样，则报警，记录机会。
  # 3. 如果当前的K线，最低价和收盘价穿过压力，或者最高价和收盘价穿过支撑，则报警。并且记录穿过的时间和收盘价格。

  last_oppo = post_db.run_sql_to_dict_list(get_last_oppo_sql({
     'symbol': symbol
  }))

  last_oppo = last_oppo[0] if last_oppo.__len__() > 0 else None

  current_close_price = df.iloc[-1]['close']
  current_high_price = df.iloc[-1]['high']
  current_low_price = df.iloc[-1]['low']
  current_close_price_time = df.index[-1]

  # print(type(nearest_low_line))
  # print(type(last_oppo['nearest_low_line']))

  # print(type(nearest_high_line))
  # print(type(last_oppo['nearest_high_line']))

  # 1. 如果还没创建过数据，且产生新的机会，则报警，记录机会。
  if last_oppo is None and is_need is True and (nearest_high_line is not None or nearest_low_line is not None):
    sql = post_sql({
      'symbol': symbol,
      'symbol_type': 'crypto',
      'interval': '15m',
      'symbol_title': '比特币永续合约',
      'start_time': unix_ms_timestamp_to_date_string(startTime),
      'end_time': unix_ms_timestamp_to_date_string(endTime),
      'nearest_high_line': nearest_high_line if nearest_high_line else 'NULL',
      'nearest_low_line': nearest_low_line if nearest_low_line else 'NULL',
      'strategy_name': '标准突破',
      'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      # 'close_price': current_close_price,
      # 'close_price_time': current_close_price_time
    })
    post_db.run_sql_to_commit(sql)
    send_email(f"{current_close_price_time}【{symbol}进入盘整】阻力{nearest_high_line} 支撑{nearest_low_line}", '查看', "513909280@qq.com")

  if nearest_low_line and current_high_price > nearest_low_line and current_close_price < nearest_low_line:
    post_db.run_sql_to_commit(update_breakout_low_price({
      'id': last_oppo['id'],
      'breakout_low_line_price': current_close_price,
      'breakout_low_line_time': current_close_price_time
    }))
    send_email(f"{current_close_price_time}【{symbol}价格穿过支撑】{current_close_price} 穿过 {nearest_low_line}", '查看', "513909280@qq.com")

  elif nearest_high_line and current_low_price < nearest_high_line and current_close_price > nearest_high_line:
    post_db.run_sql_to_commit(update_breakout_high_price({
      'id': last_oppo['id'],
      'breakout_high_line_price': current_close_price,
      'breakout_high_line_time': current_close_price_time
    }))
    send_email(f"{current_close_price_time}【{symbol}价格穿过阻力{current_close_price} 穿过 {nearest_high_line}", '查看', "513909280@qq.com")

  elif last_oppo and (
     (nearest_low_line and last_oppo['nearest_low_line'] and str(round(nearest_low_line,5)) != str(round(last_oppo['nearest_low_line'],5)))
     or (nearest_high_line and last_oppo['nearest_high_line'] and str(round(nearest_high_line,5)) != str(round(last_oppo['nearest_high_line'],5)))
     ) and is_need is True:
    sql = post_sql({
      'symbol': symbol,
      'symbol_type': 'crypto',
      'interval': '15m',
      'symbol_title': '比特币永续合约',
      'start_time': unix_ms_timestamp_to_date_string(startTime),
      'end_time': unix_ms_timestamp_to_date_string(endTime),
      'nearest_high_line': nearest_high_line if nearest_high_line else 'NULL',
      'nearest_low_line': nearest_low_line if nearest_low_line else 'NULL',
      'strategy_name': '标准突破',
      'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      # 'close_price': current_close_price,
      # 'close_price_time': current_close_price_time
    })
    post_db.run_sql_to_commit(sql)
    send_email(f"{current_close_price_time}【{symbol}阻力和支撑发生变化】阻力{nearest_high_line} 支撑{nearest_low_line}",
               f"旧阻力{last_oppo['nearest_high_line']} 旧支撑{last_oppo['nearest_low_line']}", "513909280@qq.com")



  # # time.sleep(1)

