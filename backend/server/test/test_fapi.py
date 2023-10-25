import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))
from binance.um_futures import UMFutures

from utils.date import unix_ms_timestamp_to_date_string, date_string_to_unix_ms_timestamp

print(unix_ms_timestamp_to_date_string(1695676380000))
print(date_string_to_unix_ms_timestamp('2023-09-25 21:13:00', timezone='UTC'))

api_key = 'dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB'
secret_key = 'lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5'

um_futures_client = UMFutures(key=api_key, secret=secret_key)

# Get account information
# print(um_futures_client.account())

# Get account information
print(um_futures_client.continuous_klines(
  pair='BTCUSDT',
  contractType='PERPETUAL',
  startTime=1641095256000,
  endTime=1641181656000,
  interval='1d')
)

# # Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.0002,
#     'price': 59808
# }

# response = cm_futures_client.new_order(**params)
# print(response)