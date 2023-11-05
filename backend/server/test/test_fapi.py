import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

sys.path.append(os.path.dirname(script_dir))
from binance.um_futures import UMFutures

from utils.date import date_string_to_unix_ms_timestamp, unix_ms_timestamp_to_date_string, get_current_date, get_delta_date

print(unix_ms_timestamp_to_date_string(1695676380000))
print(date_string_to_unix_ms_timestamp('2023-09-25 21:13:00', timezone='UTC'))

api_key = 'dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB'
secret_key = 'lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5'

um_futures_client = UMFutures(key=api_key, secret=secret_key)

# Get account information
# print(um_futures_client.account())

# Get account information
startTime = date_string_to_unix_ms_timestamp(f"{get_delta_date(minutes=60*100)}")
endTime = date_string_to_unix_ms_timestamp(f"{get_current_date()}")

data_list = um_futures_client.continuous_klines(
  pair='BTCUSDT',
  contractType='PERPETUAL',
  startTime=1697400000000 - 60 * 60 * 1000 * 100,
  endTime=1697400000000,
  interval='1h')

new = [[data[0], data[1], data[2], data[3], data[4], data[5]] for data in data_list]

print(new)

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