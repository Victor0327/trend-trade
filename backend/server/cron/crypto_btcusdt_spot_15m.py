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
from binance.api import API as BinanceAPI
from table.t_crypto_insert import get_insert_sql, create_table_and_index_sql
from service.postgres_engine import post_db

from utils.date import date_string_to_unix_ms_timestamp, get_current_date, get_delta_date



class CronJob:
  job_id = 'crypto_btcusdt_spot_15m'
  trigger = 'cron'
  trigger_args = {
    'hour': '*',
    'minute': '*/15',
    'second': 0
  }

  def __init__(self):
    pass

  def run(self):
    logging.info('start cron job crypto_btcusdt_spot_15m')
    api_key = 'Nd0C1zQ4YpMyhEl30xPzkHkM43RjC39QLg9UoJjSU8TmymY8WgBoBB4d4X6X4MtX'
    secret_key = 'Xc0CnHSdd3RgjgIySPC5Ofg7QkajMA98qaGFomV6J6NmuTVsOSWRJ5ykOkTR2ssa'

    # 临时本地执行不需要代理
    proxies = {
      'http': 'http://10.0.8.16:7890',
      'https': 'http://10.0.8.16:7890',
    }

    futures_client = BinanceAPI(
      base_url="https://api.binance.com",
      key=api_key,
      secret=secret_key,
      proxies=proxies
    )


    symbol = 'BTCUSDT'
    interval = '15m'

    # 每天utc8 早上8点开始跑昨天一天的数据
    # 应该是昨天的8点到今天的7点59分59秒
    # endtime 改到今天的8点整 这样今天的临时数据也能跑出来
    startTime = date_string_to_unix_ms_timestamp(f"{get_delta_date(format='%Y-%m-%d', days=1)} 08:00:00")
    endTime = date_string_to_unix_ms_timestamp(f"{get_current_date(format='%Y-%m-%d')} 08:00:00")

    # startTime = date_string_to_unix_ms_timestamp("2023-02-05 08:00:00")
    # endTime = date_string_to_unix_ms_timestamp("2023-10-04 08:00:00")


    limit = 10

    # Get account information
    data_list = futures_client.query(
      url_path=f'/api/v3/klines?symbol={symbol}&interval={interval}&startTime={startTime}&endTime={endTime}&limit={limit}',
    )

    logging.info(data_list)
    # print(data_list)

    sql = get_insert_sql({
      'pair': symbol.lower(),
      'contractType': 'spot',
      'interval': interval.lower()
    }, data_list)

    logging.info(sql)

    post_db.run_sql_to_commit(sql)

    # params = {
    #   'symbol': symbol,
    #   'contractType': 'spot',
    #   'interval': interval,
    # }

    # create_table_sql = create_table_and_index_sql(params)

    # post_db.run_sql_to_commit(create_table_sql)

job = CronJob()

# 临时要执行
# job.run()