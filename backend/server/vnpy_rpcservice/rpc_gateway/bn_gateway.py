import logging
import json
from typing import List
from vnpy.event import EventEngine
from vnpy.rpc import RpcServer
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.constant import Exchange
from vnpy.trader.object import (
    TickData,
    BarData,
    Interval,
    SubscribeRequest,
    HistoryRequest
)
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient as Client
from binance.um_futures import UMFutures
from threading import Thread
import datetime

class BinanceRpcGateway(BaseGateway):
    """
    用于通过RPC发布币安的Tick数据的Gateway。
    """

    def __init__(self, event_engine, gateway_name="BINANCE"):
        super().__init__(event_engine, gateway_name)
        self.um_futures = UMFutures(
            key='dT8HdA1qXn0M7g7d4fB2i1BRKztf1JVMjqJi7lFFmUwIEmaa3kPek1Sagkzpy5DB',
            secret='lIjlxlps2YV4VxjDCrIDOsGdHkJ16YpPvQ6jVfDhifLyR9Dag4sIrtxI2BYaL3l5',
            )

    def connect(self, setting: dict):
        """
        连接到API并启动数据推送。
        """
        self.client = Client(on_message=self.message_handler)

    def close(self):
        pass

    def send_order(self, req):
        pass

    def cancel_order(self, req):
        pass

    def query_account(self):
        pass

    def query_position(self):
        pass

    # req
    # symbol: str
    # exchange: Exchange
    # start: datetime
    # end: datetime = None
    # interval: Interval = None
    def query_history(self, req: HistoryRequest) -> List[BarData]:
        print('=============')

        def fetch_data(startTime, endTime):

            return self.um_futures.klines(
                symbol=req.symbol,
                interval=req.interval.value,
                startTime=startTime,
                endTime=endTime,
                limit=1500
            )

        start_time = int(req.start.timestamp()) * 1000
        end_time = int(req.end.timestamp()) * 1000


        next_start_time = start_time
        data_list = []
        while next_start_time < end_time:
            tmp_data = fetch_data(next_start_time, end_time)
            last_end_time = tmp_data[-1][0]
            next_start_time = last_end_time + 60 * 1000
            data_list = data_list + tmp_data



        bar_data_list = [
            BarData(
                symbol=req.symbol,
                exchange=Exchange.BINANCEFUTURES,
                datetime=datetime.datetime.fromtimestamp(data[0] / 1000),
                interval=req.interval,
                volume=data[5],
                turnover=data[7],
                open_price=data[1],
                high_price=data[2],
                low_price=data[3],
                close_price=data[4],
                gateway_name=self.gateway_name
            )
            for data in data_list
        ]

        return bar_data_list


    def subscribe(self, req: SubscribeRequest) -> None:
        self.client.agg_trade(symbol=req.symbol)



    def message_handler(self, bsm, message):
        logging.info(message)
        msg = json.loads(message)
        # print(msg)
        if 'e' in msg:
            tick = TickData(
                symbol=msg['s'],
                exchange=Exchange.BINANCEFUTURES,
                datetime=datetime.datetime.fromtimestamp(msg['E'] / 1000),
                name=msg['s'],
                volume=msg['q'],
                turnover=float(msg['q']) * float(msg['p']),
                last_price=msg['p'],
                gateway_name=self.gateway_name
            )
            self.on_tick(tick)

    def on_tick(self, tick):
        """
        当新的Tick数据到达时触发。
        """
        logging.info(tick)
        print(tick)
        self.event_engine.put(tick)