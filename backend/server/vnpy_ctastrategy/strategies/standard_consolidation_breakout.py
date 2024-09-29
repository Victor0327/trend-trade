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

from datetime import time
import pandas as pd
import numpy as np
from vnpy.trader.constant import KeyLineType, Direction, Offset, Status, Interval
from vnpy_ctastrategy.base import StopOrderStatus
from itertools import combinations
from indicator.zigzag import calculate_zigzag_indicator
from utils.math import calculate_atr
import strategy.standard as standard
import logging
import math

# 有仓位就不开仓
# 没仓位进行判断是否符合条件
# 开仓设置止损止盈 默认1:3盈亏比

# 1. 处理突破bar过长的问题,细化到1分钟bar开仓
# 如果当前价格已经突破，开始看分钟K，把最近的1分钟K线和上一根小时线合并成一根小时线。去看是否符合开仓条件

# 2. 有收益后进行利润保护。把止损逐渐抬高。
# 超过1倍盈亏比就拉平保
# 每再超过1倍就止损抬高一次

# TODO: 阿尔法因子 判断当前顺势逆势 进行增减开仓

# TradeData 重复
class StandardConsolidationBreakoutStrategy(CtaTemplate):
    """"""
    author = "用Python的交易员"

    # 每笔订单的止损金额
    fixed_risk_amount = 1000

    # 合约的单位
    size=1

    # 盘整空间
    consolidation_size=60

    # 盈亏比
    sl_tp_ratio = 30

    bar_window = 60

    # 贝塔因子 调节多空或者顺势逆势
    beta = 0

    # 当前区间的高低线
    key_high = None
    key_low = None



    parameters = ["fixed_risk_amount", "sl_tp_ratio", "consolidation_size", "bar_window", "beta"]
    variables = ["key_high", "key_low"]

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

        self.bg = BarGenerator(self.on_bar, self.bar_window, self.on_window_bar)
        self.bg_daily = BarGenerator(self.on_bar, interval=Interval.DAILY, on_window_bar=self.on_daily_bar, daily_end=time(8, 0, 0))
        self.am = ArrayManager(size=self.consolidation_size)
        self.am_daily = ArrayManager(size=60)


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

    def open_position_by_signal(self, breakout, bar: BarData):
        if breakout is True:
          print('穿过阻力', self.key_high, self.key_low, bar.low_price, bar.high_price, self.cta_engine.datetime)
          # print('ma60', self.am_daily.sma(60), self.cta_engine.datetime)

          daily_sma_60 = self.am_daily.sma(60)
          # 开仓仓位 = 每笔止损金额 / (预估开仓成交价 - 止损价)
          if math.isnan(daily_sma_60) is not True and bar.close_price > daily_sma_60:
            position = round((1 + self.beta) * self.fixed_risk_amount / abs( bar.close_price - self.key_low), 2)
          elif math.isnan(daily_sma_60) is not True and bar.close_price < daily_sma_60:
            position = round((1 - self.beta) * self.fixed_risk_amount / abs( bar.close_price - self.key_low), 2)
          else:
            position = round(self.fixed_risk_amount / abs( bar.close_price - self.key_low), 2)

          self.buy(bar.high_price + 5, position)
          print('开多', bar.close_price, self.cta_engine.datetime, position)
          # 前一个低点设置止损
          print('开多止损', self.key_low)
          self.send_order(
            direction=Direction.SHORT,
            offset=Offset.CLOSE,
            price=self.key_low,
            volume=position,
            stop=True
          )
        elif breakout is False:
          print('穿过支撑', self.key_high, self.key_low, bar.low_price, bar.high_price, self.cta_engine.datetime)

          daily_sma_60 = self.am_daily.sma(60)
          # 开仓仓位 = 每笔止损金额 / (预估开仓成交价 - 止损价)
          if math.isnan(daily_sma_60) is not True and bar.close_price > daily_sma_60:
            position = round((1 - self.beta) * self.fixed_risk_amount / abs( bar.close_price - self.key_high), 2)
          elif math.isnan(daily_sma_60) is not True and bar.close_price < daily_sma_60:
            position = round((1 + self.beta) * self.fixed_risk_amount / abs( bar.close_price - self.key_high), 2)
          else:
            position = round(self.fixed_risk_amount / abs( bar.close_price - self.key_high), 2)

          self.short(bar.low_price - 5, position)
          print('开空', bar.close_price, self.cta_engine.datetime, position)
          # 前一个低点设置止损
          print('开空止损', self.key_high)
          self.send_order(
            direction=Direction.LONG,
            offset=Offset.CLOSE,
            price=self.key_high,
            volume=position,
            stop=True
          )
        else:
          pass

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)
        self.bg_daily.update_bar(bar)

        # 当前没有持仓且价格突破震荡
        if self.pos == 0:
          if self.key_high is not None and self.key_low is not None and (bar.close_price > self.key_high or bar.close_price < self.key_low):
              if self.bg.window_bar is not None:
                # print('时间', self.cta_engine.datetime, 'on_bar', self.bg.window_bar)
                breakout = standard.is_breakout_consolidation_k_lines(self.am, self.key_high, self.key_low, self.bg.window_bar, is_window_close=False)
                self.open_position_by_signal(breakout, bar)
                pass
        else:
        # 当前有持仓，且价格超过止损的一倍空间，把止损提高到开仓为止。
          trades = self.cta_engine.get_all_trades()
          last_trade = trades[-1]
          if last_trade.offset == Offset.OPEN:
            if last_trade.offset == Offset.OPEN and last_trade.direction == Direction.LONG:
              pnl = (bar.close_price - last_trade.price) * last_trade.volume
              sl = self.fixed_risk_amount / last_trade.volume
              tp_risk_amount = pnl // self.fixed_risk_amount
              new_sl_price = last_trade.price + sl * (tp_risk_amount - 1)

              # 已经设置过此止损，跳过
              has_stop_order_set = False
              for stop_order in self.cta_engine.active_stop_orders.values():
               if stop_order.vt_symbol == f'{last_trade.symbol}.{last_trade.exchange.value}' and stop_order.offset == Offset.CLOSE:
                  # print('stop_order.price', stop_order.price)
                  # print('new_sl_price', new_sl_price)
                  if abs(stop_order.price - new_sl_price) < 1:
                    has_stop_order_set = True
                    break

              if tp_risk_amount > 0 and has_stop_order_set is False:
                print('移动止损', new_sl_price)
                self.send_order(
                  direction=Direction.SHORT,
                  offset=Offset.CLOSE,
                  price=new_sl_price,
                  volume=last_trade.volume,
                  stop=True
                )
            elif last_trade.offset == Offset.OPEN and last_trade.direction == Direction.SHORT:
              pnl = (last_trade.price - bar.close_price) * last_trade.volume
              sl = self.fixed_risk_amount / last_trade.volume
              tp_risk_amount = pnl // self.fixed_risk_amount
              new_sl_price = last_trade.price - sl * (tp_risk_amount - 1)

              # 已经设置过此止损，跳过
              has_stop_order_set = False
              for stop_order in self.cta_engine.active_stop_orders.values():
               if stop_order.vt_symbol == f'{last_trade.symbol}.{last_trade.exchange.value}' and stop_order.offset == Offset.CLOSE:
                  print('stop_order.price', stop_order.price)
                  print('new_sl_price', new_sl_price)
                  if abs(stop_order.price - new_sl_price) < 1:
                    has_stop_order_set = True
                    break

              if tp_risk_amount > 0 and has_stop_order_set is False:
                print('移动止损', new_sl_price)
                self.send_order(
                  direction=Direction.LONG,
                  offset=Offset.CLOSE,
                  price=new_sl_price,
                  volume=last_trade.volume,
                  stop=True
                )

    def on_daily_bar(self, bar: BarData):
       self.am_daily.update_bar(bar)
       pass


    def on_window_bar(self, bar: BarData):
        """"""
        # self.cancel_all()

        am = self.am
        am.update_bar(bar)

        if not am.inited:
            return

        # print(self.pos)
        if self.pos == 0:
          result, real_body_max_high, real_body_min_low = standard.is_narrow_consolidation_k_bars(
             self.am,
             offset=-3,
             real_body_each_range=2,
             real_body_gradient_range=2,
             real_body_total_range=2,
             glitch_range=1
             )
          if result is True:
            # 设置关键位置
            self.key_high = real_body_max_high
            self.key_low = real_body_min_low

            # print('时间', self.cta_engine.datetime, 'on_window_bar', bar)
            breakout = standard.is_breakout_consolidation_k_lines(am, real_body_max_high, real_body_min_low, bar, is_window_close=True)
            self.open_position_by_signal(breakout, bar)
          else:
            # 当前不是窄幅震荡，清空关键位置
            self.key_high = None
            self.key_low = None
          pass

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
                tp_price = trade.price + (trade.price - sl_price) * self.sl_tp_ratio
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
                tp_price = trade.price - (sl_price - trade.price) * self.sl_tp_ratio
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

          trades = self.cta_engine.get_all_trades()
          cur_trade = trade
          last_trade = trades[-1]
          if last_trade.direction == Direction.LONG:
            pnl = (cur_trade.price - last_trade.price) * cur_trade.volume
          else:
            pnl = - (cur_trade.price - last_trade.price) * cur_trade.volume
          print('平仓损益', pnl, cur_trade, last_trade)


          to_delete_vt_order_ids = []
          for limit_order in self.cta_engine.active_limit_orders.values():
            print(limit_order.vt_orderid)
            if f'{limit_order.symbol}.{limit_order.exchange.value}' == f'{trade.symbol}.{trade.exchange.value}' and limit_order.offset == Offset.CLOSE:
              to_delete_vt_order_ids.append(limit_order.vt_orderid)
              print('删除止盈单', limit_order)

          for stop_order in self.cta_engine.active_stop_orders.values():
             print(stop_order.stop_orderid)
             if f'{stop_order.vt_symbol}' == f'{trade.symbol}.{trade.exchange.value}' and stop_order.offset == Offset.CLOSE:
              to_delete_vt_order_ids.append(stop_order.stop_orderid)
              print('删除止损单', stop_order)

          for vt_orderid in to_delete_vt_order_ids:
            self.cancel_order(vt_orderid)



        # {'gateway_name': 'BACKTESTING', 'symbol': 'BTCUSDT', 'exchange': <Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>, 'orderid': '1', 'tradeid': '1', 'direction': <Direction.LONG: '多'>, 'offset': <Offset.OPEN: '开'>, 'price': 27297.0, 'volume': 1000, 'datetime': datetime.datetime(2023, 10, 4, 9, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')), 'vt_symbol': 'BTCUSDT.BINANCEFUTURES', 'vt_orderid': 'BACKTESTING.1', 'vt_tradeid': 'BACKTESTING.1'}
        # {'gateway_name': 'BACKTESTING', 'symbol': 'BTCUSDT', 'exchange': <Exchange.BINANCEFUTURES: 'BINANCEFUTURES'>, 'orderid': '2', 'tradeid': '2', 'direction': <Direction.SHORT: '空'>, 'offset': <Offset.CLOSE: '平'>, 'price': 27123.0, 'volume': 1000, 'datetime': datetime.datetime(2023, 10, 11, 10, 34, tzinfo=zoneinfo.ZoneInfo(key='Asia/Shanghai')), 'vt_symbol': 'BTCUSDT.BINANCEFUTURES', 'vt_orderid': 'BACKTESTING.2', 'vt_tradeid': 'BACKTESTING.2'}


        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        print('on_stop_order', stop_order)
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
