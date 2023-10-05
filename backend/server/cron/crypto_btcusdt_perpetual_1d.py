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
from table.t_crypto_insert import get_insert_sql
from service.postgres_engine import post_db

from utils.date import date_string_to_unix_ms_timestamp, get_current_date, get_delta_date

class CronJob:
  job_id = 'crypto_btcusdt_perpetual_1d'
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
    logging.info('start cron job crypto_btcusdt_perpetual_1d')
    api_key = 'Nd0C1zQ4YpMyhEl30xPzkHkM43RjC39QLg9UoJjSU8TmymY8WgBoBB4d4X6X4MtX'
    secret_key = 'Xc0CnHSdd3RgjgIySPC5Ofg7QkajMA98qaGFomV6J6NmuTVsOSWRJ5ykOkTR2ssa'

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


    pair = 'BTCUSDT'
    contractType = 'PERPETUAL'
    interval = '1d'


    # 每天utc8 早上8点开始跑昨天一天的数据
    # 应该是昨天的8点到今天的7点59分59秒
    startTime = date_string_to_unix_ms_timestamp(f"{get_delta_date(format='%Y-%m-%d', days=1)} 08:00:00")
    endTime = date_string_to_unix_ms_timestamp(f"{get_current_date(format='%Y-%m-%d')} 08:00:00")

    # print(f"{get_delta_date(format='%Y-%m-%d', days=1)} 08:00:00")
    # print(f"{get_current_date(format='%Y-%m-%d')} 07:59:59")

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

job = CronJob()

# 临时要执行
# job.run()