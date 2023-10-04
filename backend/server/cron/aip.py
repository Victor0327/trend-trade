# import sys
# import os

# # 获取当前脚本的绝对路径
# script_path = os.path.abspath(__file__)
# # 获取当前脚本所在的目录路径
# script_dir = os.path.dirname(script_path)

# sys.path.append(os.path.dirname(script_dir))

import logging
from typing import List
from service.postgres_engine import post_db
from utils.date import get_current_date, get_delta_date
from utils.math import average, round_decimal
from service.qy_weixin import qy_weixin
from service.email import send_email

from table.aip import get_aip_list_sql, get_symbol_today_price_sql, get_symbol_close_price_list_sql

# {'id': 1,
#  'symbol': 'btcusdt_spot',
#  'first_invest_money': Decimal('10000.000'),
#  'invest_cron_day': 6,
#  'invest_cron_hour': 13,
#  'invest_money': Decimal('1500.000'),
#  'invest_increase_coefficient': Decimal('2.000'),
#  'price_area': 'panic',
#  'underestimated_coefficient': Decimal('1.250'),
#  'greedy_coefficient': Decimal('2.500'),
#  'current_invest_total_money': Decimal('10000.000'),
#  'current_invest_total_position': Decimal('0.350000'),
#  'current_average_cost': Decimal('28000.000'),
#  'currency': 'usd',
#  'delete_flag': False,
#  'invest_cron_minute': 0,
#  'symbol_type': 'crypto'
# }

class AipCronJob:
  job_id: str
  trigger: str
  trigger_args: dict
  aip: dict

  def __init__(self, job_id, trigger, trigger_args, aip):
    self.job_id = job_id
    self.trigger = trigger
    self.trigger_args = trigger_args
    self.aip = aip

  def run(self):
    logging.info('start cron job aip')
    underestimated_coefficient = self.aip['underestimated_coefficient']
    greedy_coefficient = self.aip['greedy_coefficient']
    invest_increase_coefficient = self.aip['invest_increase_coefficient']
    invest_money = self.aip['invest_money']
    currency = self.aip['currency']

    symbol = self.aip['symbol']
    symbol_type = self.aip['symbol_type']

    table_name = f"{symbol_type}_{symbol}_1d"

    # 拿当天的价格 crypto 是从bn拿的,时间是utc时间转成了北京时间
    if symbol_type == 'crypto':
      start_time = f"{get_current_date(format='%Y-%m-%d')} 08:00:00"
    else:
      start_time = f"{get_current_date(format='%Y-%m-%d')} 00:00:00"

    today_price_args = {
      'table_name': table_name,
      'start_time': start_time
    }

    today_price = post_db.run_sql_to_dict_list(get_symbol_today_price_sql(today_price_args))[0]['close']
    logging.info(today_price)

    args = {
      'table_name': table_name,
      'start_time': f"{get_delta_date(format='%Y-%m-%d', days=200)} 08:00:00",
      'end_time': f"{get_current_date(format='%Y-%m-%d')} 07:59:59",
    }
    close_price_list = post_db.run_sql_to_tuple_list(get_symbol_close_price_list_sql(args))
    close_values = [item[0] for item in close_price_list]
    close_values_ma_200 = average(close_values)

    if today_price <= close_values_ma_200:
      current_invest_money = round_decimal(invest_increase_coefficient * invest_money)
      message = f"【{symbol}定期投资提醒】,今日价格{today_price}处于恐慌区，买入{current_invest_money}{currency}。"
    elif today_price > close_values_ma_200 and today_price <= close_values_ma_200 * underestimated_coefficient:
      current_invest_money = round_decimal(invest_money)
      message = f"【{symbol}定期投资提醒】,今日价格{today_price}处于低估区，买入{current_invest_money}{currency}。"
    elif today_price > close_values_ma_200 * underestimated_coefficient and today_price <= close_values_ma_200 * greedy_coefficient:
      current_invest_money = 0
      message = f"【{symbol}定期投资提醒】,今日价格{today_price}处于正常区，买入{current_invest_money}{currency}。"
    elif today_price > close_values_ma_200 * greedy_coefficient:
      message = f"【{symbol}定期投资提醒】,今日价格{today_price}处于贪婪区，请分批卖出。"

    qy_weixin.send_message(message)
    send_email(f"【{symbol}定期投资提醒】", message, "513909280@qq.com")


aip_list = post_db.run_sql_to_dict_list(get_aip_list_sql())

aip_cron_jobs: List[AipCronJob] = []

for aip in aip_list:
  job_id = f"aip_{aip['id']}"
  trigger = 'cron'
  trigger_args = {
    'day': aip['invest_cron_day'],
    'hour': aip['invest_cron_hour'],
    'minute': aip['invest_cron_minute'],
    'day': aip['invest_cron_day'],
    # 'hour': 23,
    # 'minute': 7,
    # 'second': 0
  }
  aip_cron_job = AipCronJob(job_id, trigger, trigger_args, aip)
  aip_cron_jobs.append(aip_cron_job)