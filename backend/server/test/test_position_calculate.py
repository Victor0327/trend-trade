import sys
import os
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))

from controller.position_calculate import calculate

# MA
# args = {
#   'entry_price': 2300,
#   'sl_price': 2400,
#   'tp_price': 2200,
#   'risk_amount': 2000,
#   'margin_level': 0.1,
#   'symbol': 'MA0',
#   'symbol_type': 'cn_goods'
# }

# print(calculate(args))

# # CHFJPY
args = {
  'symbol': 'CHFJPY',
  'symbol_type': 'currency',
  'entry_price': 165,
  'sl_price': 165.1,
  'tp_price': 165.2,
  'risk_amount': 0.67,
  'margin_level': 0.005,
}

print(calculate(args))

# GBPUSD
args = {
  'entry_price': 1.23,
  'sl_price': 1.23909,
  'tp_price': 1.222,
  'risk_amount': 100,
  'margin_level': 0.001,
  'symbol': 'GBPUSD',
  'symbol_type': 'currency'
}

print(calculate(args))