import sys
import os
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))

import json
from controller.trade_record import trade_record



# get

def get(args):

  trade_record.get_trade_record(args)

def get_cumulative_sum(args):

  trade_record.get_cumulative_sum(args)

# insert
def insert(args):
  with open(f'{script_dir}/create_trade_record.json', 'r') as file:
      data = json.load(file)

  print(trade_record.create_trade_record(args))

def close_position(args):

   with open(f'{script_dir}/close_position.json', 'r') as file:
      data = json.load(file)

   print(trade_record.close_position(args))

def delete():

    print(trade_record.delete_trade_record({
      'id': 1,
      'risk_amount_currency': 'CNY',
      'risk_amount': 2000,
    }))


# insert({
#   "risk_amount_step_id": 2,
#   "risk_amount_currency": "USD",
#   "risk_amount": 100,

#   "open_date": "2023-10-20 00:00:00",
#   "symbol_type": "us_goods",
#   "symbol": "XCT",
#   "strategy_id": 1,
#   "risk": 1,
#   "memo": "test currency",

#   "strategy_requirement_performance_array" : [
#     [1, "S", "ccc"],
#     [2, "A", "aaa"],
#   ]
# })

# delete()

# close_position({
#   "id": 2,
#   "risk_amount_currency": "USD",
#   "risk_amount": 100,

#   "close_date": "2023-10-11 00:00:00",
#   "result": -2,
#   "memo": "LOSS"
# })

# get({
#     'risk_amount_currency': 'CNY',
#     'risk_amount': 2000,
#   })

get({
    'risk_amount_currency': 'USD',
    'risk_amount': 100,
  })

get_cumulative_sum({
    'risk_amount_currency': 'USD',
    'risk_amount': 100,
    'strategy_id': 4
  })


