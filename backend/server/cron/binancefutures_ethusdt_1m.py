# 临时执行需要的代码
import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))
# =======================
import logging
import pandas as pd
import pytz
from binance.um_futures import UMFutures
from vnpy_postgresql import Database
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from datetime import datetime

from utils.date import date_string_to_unix_ms_timestamp, get_current_date, get_delta_date

db = Database()


class CronJob:
  job_id = 'binancefutures_ethusdt_1m'
  trigger = 'cron'
  # 服务器是utc时区需要调整
  trigger_args = {
    'hour': '*',
    'minute': '*/15',
    'second': 0
  }

  um_futures_client = UMFutures(
    key='dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB',
    secret='lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5',
    # proxies={
    #   'http': 'http://10.0.8.16:7890',
    #   'https': 'http://10.0.8.16:7890',
    # }
  )

  def __init__(self):
    pass

  def fetch_data(self, startTime, endTime):
    data_list = self.um_futures_client.continuous_klines(
      pair='ETHUSDT',
      contractType='PERPETUAL',
      startTime=startTime,
      endTime=endTime,
      interval='1m',
      limit=1500)

    return data_list

  def save_bar_data(self, data_list):
    bar_data_list = [
      BarData(
          symbol='ETHUSDT',
          exchange=Exchange.BINANCEFUTURES,
          datetime=datetime.fromtimestamp(row[0] / 1000),

          interval=Interval.MINUTE,
          volume=row[5],
          turnover=row[7],
          open_interest=0,
          open_price=row[1],
          high_price=row[2],
          low_price=row[3],
          close_price=row[4],
          gateway_name="BINANCEFUTURES"
      )
      for row in data_list
    ]
    db.save_bar_data(bars=bar_data_list)

  def run(self):
    logging.info('start cron job binancefutures_ethusdt_1m')


    # 每天utc8 早上8点开始跑昨天一天的数据
    # 应该是昨天的8点到今天的7点59分59秒
    startTime = date_string_to_unix_ms_timestamp('2019-09-10 00:00:00')
    endTime = date_string_to_unix_ms_timestamp(get_current_date(format='%Y-%m-%d %H:%M:%S'), timezone='UTC')



    # Get account information



    next_start_time = startTime

    while next_start_time < endTime:
      data_list = self.fetch_data(next_start_time, endTime)
      last_end_time = data_list[-1][0]
      next_start_time = last_end_time + 60000
      self.save_bar_data(data_list)


  # [1568074740000, start_time
  # '10353.89', open
  # '10355.60', high
  # '10334.62', low
  # '10355.60', close
  # '4.915', volume
  # 1568074799999, end_time
  # '50894.19763', volume_money
  # 9, volume_orders
  # '4.912', active_buy_volume
  # '50863.19258', active_buy_volume_money
  # '0']








job = CronJob()

# 临时要执行
job.run()