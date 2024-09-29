import sys
import os
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname((os.path.dirname(os.path.dirname(script_path))))

sys.path.append(script_dir)
print(sys.path)

#!/usr/bin/env python

import time
import logging
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient as Client

config_logging(logging, logging.DEBUG)


def message_handler(_, message):
    logging.info(message)


my_client = Client(on_message=message_handler)


# my_client.mini_ticker(symbol="BTCUSDT")
# my_client.mini_ticker(symbol="ETHUSDT")

time.sleep(30)

logging.debug("closing ws connection")
my_client.stop()
