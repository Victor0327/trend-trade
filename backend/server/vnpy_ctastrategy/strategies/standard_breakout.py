from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager
)

from time import time
import pandas as pd
import numpy as np
from vnpy.trader.constant import KeyLineType, Direction, Offset, Status
from vnpy_ctastrategy.base import StopOrderStatus
from itertools import combinations
from indicator.zigzag import calculate_zigzag_indicator
from utils.math import calculate_atr
import strategy.standard as standard
import logging

# 有仓位就不开仓
# 没仓位进行判断是否符合条件
# 开仓设置止损止盈 默认1:3盈亏比

class StandardBreakoutStrategy(CtaTemplate):
    """"""
    author = "用Python的交易员"

    # 每笔订单的止损金额
    fixed_risk_amount = 1000


    parameters = ["fixed_risk_amount"]
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.test_funcs = [
            self.test_market_order,
            self.test_limit_order,
            self.test_cancel_all,
            self.test_stop_order
        ]
        self.last_tick = None

        self.bg = BarGenerator(self.on_bar, 60, self.on_60min_bar)
        self.am = ArrayManager(size=200)

    def open_position_signal(self) -> int:
        """"""




        return 0

    # 返回过去300根K线是否包含关键位，如果包含，返回最近的关键位的价格和类型，以及高低点数组列表。
    def contain_key_line(self) -> (KeyLineType, float, list, list):
        if not self.am.inited:
            return None, None

        high_list = self.am.high_array[-200:]
        low_list = self.am.low_array[-200:]
        extrema = calculate_zigzag_indicator(
            high_list,
            low_list)

        # 1. 判断最近90根K有4个以上端点
        points = 4
        period_length = 300
        point = extrema[-points] if len(extrema) >= points else None
        if point is None or self.am.count - point['index'] > period_length:
          print("震荡区间不满足")
          return None, None, None, None

        # 2. 高点和低点之间存在3个点以上差距小于1/2*当下级别ATR的 200SMA
        df = pd.DataFrame({
            'high': self.am.high_array,
            'low': self.am.low_array,
            'close': self.am.close_array
        })
        atr = calculate_atr(df, period=200)
        print(atr.iloc[-1] * 3 / 4)

        highs = [item for item in extrema if item['type'] == 'high']
        lows = [item for item in extrema if item['type'] == 'low']
        high_lines, key_high_points = standard.is_difference_less_than_threshold(highs[-12:], threshold = atr.iloc[-1] * 3 / 4)
        low_lines, key_low_points = standard.is_difference_less_than_threshold(lows[-12:], threshold = atr.iloc[-1] * 3 / 4)

        if len(high_lines) == 0 or len(low_lines) == 0:
            print("缺少阻力和支持线", highs, lows)
            return None, None, None, None

        # 3. 找到最近的一条关键线
        current_price = self.am.close_array[-1]
        nearest_line = None
        nearest_line_type = None

        nearest_high_line = None
        nearest_low_line = None
        nearest_low_points = []

        if len(high_lines) > 0:
          nearest_high_line = high_lines[0]
          for high_index, high_line in enumerate(high_lines):
              if abs(high_line - current_price) < abs(nearest_high_line - current_price):
                  nearest_high_line = high_line

        if len(low_lines) > 0:
          nearest_low_line = low_lines[0]
          for low_index, low_line in enumerate(low_lines):
              if abs(low_line - current_price) < abs(nearest_low_line - current_price):
                nearest_low_line = low_line

        if nearest_high_line is not None and nearest_low_line is not None:
          if abs(nearest_high_line - current_price) < abs(nearest_low_line - current_price):
            nearest_line = nearest_high_line
            nearest_line_type = KeyLineType.OBSTACLE
          else:
            nearest_line = nearest_low_line
            nearest_line_type = KeyLineType.SUPPORT
        elif nearest_high_line is not None:
            nearest_line = nearest_high_line
            nearest_line_type = KeyLineType.OBSTACLE
        elif nearest_low_line is not None:
            nearest_line = nearest_low_line
            nearest_line_type = KeyLineType.SUPPORT

        # print(nearest_line_type, nearest_line, highs, lows)

        return nearest_line_type, nearest_line, highs, lows

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)

    # BarData(gateway_name='DB', extra=None, symbol='BTCUSDT', exchange=<Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>,
    #         datetime=datetime.datetime(2020, 9, 15, 5, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')),
    #         interval=None,
    #         volume=3693.7830000000004,
    #         turnover=39474198.8,
    #         open_interest=0.0,
    #         open_price=10675.0,
    #         high_price=10713.4,
    #         low_price=10662.7,
    #         close_price=10708.9)

    def on_60min_bar(self, bar: BarData):
        """"""
        # self.cancel_all()

        am = self.am
        am.update_bar(bar)

        if not am.inited:
            return


        # print(self.pos)
        if self.pos == 0:
          key_line_type, key_line, highs, lows = self.contain_key_line()
          if key_line_type == KeyLineType.OBSTACLE:
            # 判断当前的K线是否有效穿过关键位，K线的最低价小于关键位，收盘价大于关键位
            if bar.low_price < key_line and bar.close_price > key_line:
              # print(key_line, bar.high_price, bar.close_price, lows[-1]['price'])
              print('穿过阻力', key_line, key_line_type, bar.low_price, bar.high_price, self.cta_engine.datetime)
              print('开多', bar.high_price, self.cta_engine.datetime)
              # 开仓仓位 = 每笔止损金额 / (预估开仓成交价 - 止损价)
              position = round(self.fixed_risk_amount / ( bar.close_price - lows[-1]['price']), 2)
              self.buy(bar.high_price + 5, position)
              # 前一个低点设置止损
              print('开多止损', lows[-1]['price'])
              self.send_order(
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=lows[-1]['price'],
                volume=position,
                stop=True
              )
            else:
              print('未穿过阻力', key_line, key_line_type, bar.low_price, bar.high_price, self.cta_engine.datetime)
          elif key_line_type == KeyLineType.SUPPORT:
            if bar.high_price > key_line and bar.close_price < key_line:
              # print(key_line, bar.low_price, bar.close_price, highs[-1]['price'])
              print('穿过支撑', key_line, key_line_type, bar.low_price, bar.high_price, self.cta_engine.datetime)
              print('开空', bar.low_price, self.cta_engine.datetime)
              print('开空止损', highs[-1]['price'])
              # 开仓仓位 = 每笔止损金额 / (预估开仓成交价 - 止损价)
              position = round(self.fixed_risk_amount / (highs[-1]['price'] - bar.close_price), 2)
              self.short(bar.low_price - 5, position)
              # 前一个高点设置止损
              self.send_order(
                direction=Direction.LONG,
                offset=Offset.CLOSE,
                price=highs[-1]['price'],
                volume=position,
                stop=True
              )
            else:
              print('未穿过支撑', key_line, key_line_type, bar.low_price, bar.high_price, self.cta_engine.datetime)





          # {
          #    'gateway_name': 'BACKTESTING',
          #    'symbol': 'BTCUSDT',
          #    'exchange': <Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>,
          #    'orderid': '1',
          #    'tradeid': '1',
          #    'direction': <Direction.LONG: '多'>,
          #    'offset': <Offset.OPEN: '开'>,
          #    'price': 27345.5,
          #    'volume': 1000,
          #    'datetime': datetime.datetime(2023, 10, 4, 10, 7, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')),
          #    'vt_symbol': 'BTCUSDT.BINANCEFUTURES',
          #    'vt_orderid': 'BACKTESTING.1',
          #    'vt_tradeid': 'BACKTESTING.1'
          # }

          # {
          #    'BACKTESTING.1': TradeData(
          #         gateway_name='BACKTESTING',
          #         extra=None,
          #         symbol='BTCUSDT',
          #         exchange=<Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>,
          #         orderid='1',
          #         tradeid='1',
          #         direction=<Direction.LONG: '多'>,
          #         offset=<Offset.OPEN: '开'>,
          #         price=27345.5,
          #         volume=1000,
          #         datetime=datetime.datetime(2023, 10, 4, 10, 7, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai'))
          #       )
          # }


        # print(key_line_type)
        # print(key_line)

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        print('=====trade info=====')


        print('=====trade=====', trade.__dict__)
        for order in self.cta_engine.active_stop_orders.values():
           print('=====active_stop_orders.values()=====', order.__dict__)
        for order in self.cta_engine.active_limit_orders.values():
           print('=====active_limit_orders.values()=====', order.__dict__)
        # TradeData(gateway_name='BACKTESTING', extra=None, symbol='BTCUSDT', exchange=<Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>, orderid='6', tradeid='6', direction=<Direction.SHORT: '空'>, offset=<Offset.CLOSE: '平'>, price=27674.9, volume=1000, datetime=datetime.datetime(2023, 10, 6, 18, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')))

        # case1 当前成交是开仓，根据止损设置止盈
        # trade.price是开仓价，找到这个订单对应的止损价，然后计算止盈价去设置止盈单
        if trade.offset == Offset.OPEN:
          print('开仓成交', trade.price)
          # 遍历orders，找到symbol、exchange是当前品种的，offset是平仓，status是SUBMITTING或者NOTTRADED的订单
          for stop_order in self.cta_engine.active_stop_orders.values():
            if stop_order.vt_symbol == f'{trade.symbol}.{trade.exchange.value}' and stop_order.offset == Offset.CLOSE and stop_order.status in [StopOrderStatus.WAITING]:
              sl_price = stop_order.price
              if trade.direction == Direction.LONG:
                tp_price = trade.price + (trade.price - sl_price) * 3
                  # 发送止盈单
                print('发送止盈单', Direction.SHORT, tp_price)
                self.send_order(
                    direction=Direction.SHORT,
                    offset=Offset.CLOSE,
                    price=tp_price,
                    volume=trade.volume,
                    stop = False
                  )
              else:
                tp_price = trade.price - (sl_price - trade.price) * 3
                  # 发送止盈单
                print('发送止盈单', Direction.LONG, tp_price)
                self.send_order(
                    direction=Direction.LONG,
                    offset=Offset.CLOSE,
                    price=tp_price,
                    volume=trade.volume,
                    stop = False
                  )
        # case2 当前成交是平仓，把当前品种所有的平仓订单撤销
        elif trade.offset == Offset.CLOSE:
          print('平仓成交', trade.price)
          to_delete_orders = []
          for limit_order in self.cta_engine.active_limit_orders.values():
            if f'{limit_order.symbol}.{limit_order.exchange.value}' == f'{trade.symbol}.{trade.exchange.value}' and limit_order.offset == Offset.CLOSE:
              to_delete_orders.append(limit_order.vt_orderid)
          for vt_orderid in to_delete_orders:
            print('删除止盈单', vt_orderid)
            self.cancel_order(vt_orderid)
        # {'gateway_name': 'BACKTESTING', 'symbol': 'BTCUSDT', 'exchange': <Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>, 'orderid': '1', 'tradeid': '1', 'direction': <Direction.LONG: '多'>, 'offset': <Offset.OPEN: '开'>, 'price': 27297.0, 'volume': 1000, 'datetime': datetime.datetime(2023, 10, 4, 9, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')), 'vt_symbol': 'BTCUSDT.BINANCEFUTURES', 'vt_orderid': 'BACKTESTING.1', 'vt_tradeid': 'BACKTESTING.1'}
        # {'gateway_name': 'BACKTESTING', 'symbol': 'BTCUSDT', 'exchange': <Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>, 'orderid': '2', 'tradeid': '2', 'direction': <Direction.SHORT: '空'>, 'offset': <Offset.CLOSE: '平'>, 'price': 27123.0, 'volume': 1000, 'datetime': datetime.datetime(2023, 10, 11, 10, 34, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')), 'vt_symbol': 'BTCUSDT.BINANCEFUTURES', 'vt_orderid': 'BACKTESTING.2', 'vt_tradeid': 'BACKTESTING.2'}


        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        self.put_event()

    def test_market_order(self):
        """"""
        self.buy(self.last_tick.limit_up, 1)
        self.write_log("执行市价单测试")

    def test_limit_order(self):
        """"""
        self.buy(self.last_tick.limit_down, 1)
        self.write_log("执行限价单测试")

    def test_stop_order(self):
        """"""
        self.buy(self.last_tick.ask_price_1, 1, True)
        self.write_log("执行停止单测试")

    def test_cancel_all(self):
        """"""
        self.cancel_all()
        self.write_log("执行全部撤单测试")
