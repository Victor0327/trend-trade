# 临时执行需要的代码
# import sys
# import os

# # 获取当前脚本的绝对路径
# script_path = os.path.abspath(__file__)
# # 获取当前脚本所在的目录路径
# script_dir = os.path.dirname(script_path)

# sys.path.append(os.path.dirname(script_dir))
# =======================
import logging
from binance.um_futures import UMFutures
from table.t_crypto_insert import get_insert_sql, create_table_and_index_sql
from service.postgres_engine import post_db

from utils.date import date_string_to_unix_ms_timestamp, get_current_date, get_delta_date

class CronJob:
  job_id = 'crypto_ethusdt_perpetual_1d'
  trigger = 'cron'
  # 服务器是utc时区需要调整
  trigger_args = {
    'hour': 0,
    'minute': 1,
    'second': 0
  }

  def __init__(self):
    pass

  def run(self):
    logging.info('start cron job crypto_ethusdt_perpetual_1d')
    api_key = 'dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB'
    secret_key = 'lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5'

    # 临时本地执行不需要代理
    proxies = {
      'http': 'http://10.0.8.16:7890',
      'https': 'http://10.0.8.16:7890',
    }


    um_futures_client = UMFutures(
      key=api_key,
      secret=secret_key,
      proxies=proxies
    )


    pair = 'ETHUSDT'
    contractType = 'PERPETUAL'
    interval = '1d'


    # 每天utc8 早上8点开始跑昨天一天的数据
    # 应该是昨天的8点到今天的7点59分59秒
    startTime = date_string_to_unix_ms_timestamp(f"{get_delta_date(format='%Y-%m-%d', days=1)} 08:00:00")
    endTime = date_string_to_unix_ms_timestamp(f"{get_current_date(format='%Y-%m-%d')} 08:00:00")

    # startTime = date_string_to_unix_ms_timestamp("2013-01-01 08:00:00")
    # endTime = date_string_to_unix_ms_timestamp("2024-01-01 08:00:00")

    # Get account information
    data_list = um_futures_client.continuous_klines(
      pair=pair,
      contractType=contractType,
      startTime=startTime,
      endTime=endTime,
      interval=interval,
      limit=1500)

    sql = get_insert_sql({
      'pair': pair.lower(),
      'contractType': contractType.lower(),
      'interval': interval.lower()
    }, data_list)

    logging.info(sql)

    post_db.run_sql_to_commit(sql)

    # params = {
    #   'symbol': pair,
    #   'contractType': contractType,
    #   'interval': interval,
    # }

    # create_table_sql = create_table_and_index_sql(params)
    # post_db.run_sql_to_commit(create_table_sql)

job = CronJob()

# 临时要执行
# job.run()