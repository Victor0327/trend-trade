import sys
import os
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname((os.path.dirname(os.path.dirname(script_path))))

sys.path.append(script_dir)
print(sys.path)

import logging
import json
from vnpy.event import EventEngine
from vnpy.rpc import RpcServer
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.constant import Exchange
from vnpy.trader.object import TickData, SubscribeRequest, HistoryRequest, Interval, Exchange
from vnpy.trader.database import DB_TZ
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient as Client
from threading import Thread
import datetime
from vnpy_rpcservice.rpc_gateway.bn_gateway import BinanceRpcGateway


# 加载历史k线的调用关系。
# strategy 的 ABC -> cta_engine.load_bar -> main_engine.query_history -> gateway.query_history
if __name__ == "__main__":
    # 初始化事件引擎和RPC服务
    event_engine = EventEngine()
    bn_gateway = BinanceRpcGateway(event_engine)

    # 启动RPC服务器
    bn_gateway.connect()
    # bn_gateway.subscribe(SubscribeRequest(
    #     symbol='BTCUSDT',
    #     exchange=Exchange.BINANCEFUTURES
    # ))
    end = datetime.datetime.now(DB_TZ)
    start = end - datetime.timedelta(3)
    data = bn_gateway.query_history(
            HistoryRequest(
                symbol='BTCUSDT',
                exchange=Exchange.BINANCEFUTURES,
                interval=Interval.MINUTE,
                start=start,
                end=end,
            )
        )
    print(data[0])

    # 在这里可以添加更多的逻辑，例如管理RPC服务或处理其他任务
