# 临时执行需要的代码
# import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

# sys.path.append(os.path.dirname(script_dir))
# =======================
import requests
import re
import pytz
import json
import logging
from datetime import datetime, timedelta, date
from table.t_us_goods_insert import get_insert_sql, create_table_and_index_sql
from service.postgres_engine import post_db

def fetch_data(symbol):
  interval = 15
  logging.info(f'正在处理: {symbol} {interval}')

  url = f"https://gu.sina.cn/ft/api/jsonp.php/var%20_{symbol}_{interval}=/GlobalService.getMink?symbol={symbol}&type={interval}"


  response = requests.request("GET", url)
  data_str = response.content.decode('utf-8')
  print(data_str)
  match = re.search(rf'_{symbol}_{interval}=\((.*?)\);', data_str, re.DOTALL)

  if match:
      logging.info(f'数据返回成功')
      json_str = match.group(1)
      data_list = json.loads(json_str)
      # 做一个过滤 截取当天的数据
      # 获得当前日期和时间
      tz = pytz.timezone('Asia/Shanghai')
      now = datetime.now(tz)
      current_hour = now.strftime('%Y-%m-%d %H')
      last_hour_time = now - timedelta(hours=1)
      last_hour = last_hour_time.strftime('%Y-%m-%d %H')

      # 只取当前小时和上一个小时的数据
      filtered_data_list = [x for x in data_list if current_hour in x['d'] or last_hour in x['d']]

      params = {
          'symbol': symbol,
          'interval': interval
      }

      logging.info('filtered_data_list')
      logging.info(filtered_data_list)

      # insert_data_sql = get_insert_sql(params, data_list)
      # print(insert_data_sql)
      # post_db.run_sql_to_commit(insert_data_sql)

      if filtered_data_list.__len__() > 0:
        insert_data_sql = get_insert_sql(params, filtered_data_list)
        post_db.run_sql_to_commit(insert_data_sql)
  else:
      print("No match found.")



class CronJob:
    job_id = 'us_goods_sina_15'
    trigger = 'cron'
    trigger_args = {
      'hour': '*',
      'minute': '3,18,33,48',
      'second': 0
    }

    def __init__(self):
      pass

    def run(self):

      # 获取今天的日期
      today = date.today()

      # 服务器utc周末从北京时间周六早上8点开始到周一早上8点结束
      if today.weekday() >= 6:
          logging.info('今天是周日,休息啦')
          return

      logging.info('今天是工作日')

      # 打开文件并读取所有行
      # 服务器用绝对路径
      logging.info(f'打开{script_dir}/sina_us_goods.txt')
      with open(f'{script_dir}/sina_us_goods.txt', 'r') as f:
          lines = f.readlines()

      # 将每一行转换为数组的一项
      us_goods = [line.strip() for line in lines]

      for symbol in us_goods:
          fetch_data(symbol)

          # params = {
          #       'symbol': symbol,
          #       'interval': 15
          #   }
          # create_table_sql = create_table_and_index_sql(params)
          # post_db.run_sql_to_commit(create_table_sql)

job = CronJob()

# 临时要执行
# job.run()