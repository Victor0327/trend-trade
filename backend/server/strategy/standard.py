import pandas as pd
import logging
# import talib
from itertools import combinations
from utils.math import calculate_atr, slice_top_elements_from_np_array
from vnpy.trader.utility import ArrayManager
from vnpy_ctastrategy import (
    BarData
)

import numpy as np

# 小波动盘整突破，适合大盘子。小盘子由于资金对价格影响大，价格波动比较大，开仓机会少。
# 输入k bar array。判断最新K是否突破。
# 1. 最后K，开盘在两个line之间，收盘超过区间0.4%，且自身的bar高度超过0.48%
# 2. 最后的3根K合并成一根K，开盘在两个line之间，收盘超过区间0.4%，且自身的bar高度超过0.48%
# 3. 最后k的成交量超过过去10根K的平均成交量的2倍。或者最后3根K的平均成交量超过过去10根K平均成交量的2倍。
# 满足1或者2且3。则认为有效突破，然后返回突破的方向。
# True 向上 False 向下 None 未突破
# 可调参数 突破动能 0.48% 突破幅度 0.4% 成交量 2倍
# 开仓后，止损是盘整的另一端。止盈是止损的5倍。
# last_bar 可能是未结束的window_bar 也可能是结束的
def is_breakout_consolidation_k_lines(
        am: ArrayManager,
        key_high_line,
        key_low_line,
        last_window_bar: BarData,
        is_window_close: bool,
        breakout_energy=0.48,
        breakout_range=0.4,
        breakout_volume=2
        ) -> bool:
    if is_window_close:
        # window_close后 数据都进了am中
        last_bar_open = am.open_array[-1]
        last_bar_close = am.close_array[-1]
        last_bar_volume = am.volume_array[-1]

        last_3_bar_open = am.open_array[-3]
        last_3_bar_close = last_bar_close
        last_3_bar_volume = (am.volume_array[-3] + am.volume_array[-2] + am.volume_array[-1]) / 3
    else:
        # window还没close 数据还没进am
        last_bar_open = last_window_bar.open_price
        last_bar_close = last_window_bar.close_price
        last_bar_volume = last_window_bar.volume

        last_3_bar_open = am.open_array[-2]
        last_3_bar_close = last_bar_close
        last_3_bar_volume = (am.volume_array[-2] + am.volume_array[-1] + last_window_bar.volume) / 3


    condition_1_and_3 = (
        last_bar_open > key_low_line and last_bar_open < key_high_line and abs(last_bar_close - last_bar_open) / last_bar_open * 100 > breakout_energy
    ) and (
        (
            last_bar_close < key_low_line and (key_low_line - last_bar_close) / last_bar_close * 100 > breakout_range
        )
        or
        (
            last_bar_close > key_high_line and (last_bar_close - key_high_line) / key_high_line * 100 > breakout_range
        )
    ) and (
        last_bar_volume > am.volume_array[-10:].mean() * breakout_volume
    )

    condition_2_and_3 = (
        last_3_bar_open > key_low_line and last_3_bar_open < key_high_line and abs(last_3_bar_close - last_3_bar_open) / last_3_bar_open * 100 > breakout_energy
    ) and (
        (
            last_3_bar_close < key_low_line and (key_low_line - last_3_bar_close) / last_3_bar_close * 100 > breakout_range
        )
        or
        (
            last_3_bar_close > key_high_line and (last_3_bar_close - key_high_line) / key_high_line * 100 > breakout_range
        )
    ) and (
        last_3_bar_volume > am.volume_array[-10:].mean() * breakout_volume
    )

    if condition_1_and_3 or condition_2_and_3:
        if last_bar_close > key_high_line:
            return True
        else:
            return False
    else:
        # print('last_bar_close', last_bar_close, 'last_bar_open', last_bar_open)
        # print('key_low_line', key_low_line, 'key_high_line' , key_high_line)
        # print('last_bar_volume', last_bar_volume, am.volume_array[-10:].mean() * 2)
        # print('last_3_bar_volume', last_3_bar_volume, am.volume_array[-10:].mean() * 2)
        # print('last_bar_close - last_bar_open', abs(last_bar_close - last_bar_open) / last_bar_open * 100)
        # print('last_3_bar_close - last_3_bar_open', abs(last_3_bar_close - last_3_bar_open) / last_bar_open * 100)

        # print('last_bar_close - key_high_line', min(abs(last_bar_close - key_high_line), abs(last_bar_close - key_low_line)) / key_high_line * 100)
        # print('last_3_bar_close - key_high_line', min(abs(last_3_bar_close - key_high_line), abs(last_3_bar_close - key_low_line)) / key_high_line * 100)

        return None

# 输入一系列的K bar array。判断是否符合窄幅盘整结构。
# 符合的话，返回窄幅盘整的顶部和底部。
# 增加毛刺过滤，如果出现某几根K的实体最高点和最低点超过边界1%，但是第1根的开盘在区域内，第6根的收盘在区域内，则视为毛刺。
def is_narrow_consolidation_k_bars(
        am: ArrayManager,
        offset=-3,
        real_body_each_range=1,
        real_body_total_range=1,
        real_body_gradient_range=1,
        glitch_range=1
        ):

    trimmed_high_open_array, sliced_high_open_array = slice_top_elements_from_np_array(am.open_array[:offset], is_highest=True)
    open_array, sliced_low_open_array = slice_top_elements_from_np_array(trimmed_high_open_array, is_highest=False)
    sliced_max_high_open_array = np.max(sliced_high_open_array)
    sliced_min_low_open_array = np.min(sliced_low_open_array)

    trimmed_high_close_array, sliced_high_close_array = slice_top_elements_from_np_array(am.close_array[:offset], is_highest=True)
    close_array, sliced_low_close_array = slice_top_elements_from_np_array(trimmed_high_close_array, is_highest=False)
    sliced_max_high_close_array = np.max(sliced_high_close_array)
    sliced_min_low_close_array = np.min(sliced_low_close_array)

    sliced_max_high = max(sliced_max_high_open_array, sliced_max_high_close_array)
    sliced_min_low = min(sliced_min_low_open_array, sliced_min_low_close_array)



    # Calculate the entity (real body) of the K-lines
    real_body = np.abs(close_array - open_array)
    real_body_percent = real_body / open_array * 100

    np.set_printoptions(suppress=True, precision=4)





    # 每根k实体长度小于1%
    if not np.all(real_body_percent < real_body_each_range):
        return False, None, None

    # Calculate the highest and lowest points of the real body
    real_body_high = np.where(close_array > open_array, close_array, open_array)
    real_body_low = np.where(close_array > open_array, open_array, close_array)

    # print(open_array)
    # print(close_array)

    # print(real_body_high)
    # print(real_body_low)
    real_body_max_high = np.max(real_body_high)
    real_body_min_low = np.min(real_body_low)

    # 这一段实体最高和最低差距小于1%
    if (real_body_max_high - real_body_min_low) / real_body_min_low * 100 >= real_body_total_range:
        return False, None, None

    # 第一根K实体中心和最后一根K实体中心差距小于1%
    first_center = (open_array[0] + close_array[0]) / 2
    last_center = (open_array[-1] + close_array[-1]) / 2
    print(np.abs(last_center - first_center) / first_center * 100)
    if np.abs(last_center - first_center) / first_center * 100 >= real_body_gradient_range:
        return False, None, None

    # K线超过盘整区域的部分小于百分之1%则视为毛刺
    if (sliced_max_high - real_body_max_high) / real_body_max_high * 100 >= glitch_range:
        return False, None, None

    if (real_body_min_low - sliced_min_low) / real_body_min_low * 100 >= glitch_range:
        return False, None, None

    # print('sliced_max_high percent', sliced_max_high, real_body_max_high, (sliced_max_high - real_body_max_high) / real_body_max_high * 100)
    # print('sliced_min_low percent', sliced_min_low, real_body_min_low, (real_body_min_low - sliced_min_low) / real_body_min_low * 100)
    # If all conditions are met

    return True, real_body_max_high, real_body_min_low


# 输入一系列价格，如果有3个价格之间相差小于阈值，则返回这三个价格的平均值，以及这三个价格
def is_difference_less_than_threshold(prices, threshold) -> (list, list):
    lines = []
    # index price type
    points = []
    for combo in combinations(prices, 3):
        price_values = [x['price'] for x in combo]
        max_price = max(price_values)
        min_price = min(price_values)
        avg_price = sum(price_values) / 3
        diff = max_price - min_price

        # 如果3个价格之间的最大差异小于阈值，则返回True
        if diff < threshold:
            lines.append(avg_price)
            points.append(combo)

    return lines, points

# 判断是否符合系统迹象
#
def is_need_to_alert(df: pd.DataFrame, extrema, period_length=90, points=6):
    bar_len = df.__len__()
    logging.info(bar_len)
    # 1. 判断最近90根K有6个以上端点
    point = extrema[-points] if len(extrema) >= points else None
    if point is None or bar_len - point['index'] > period_length:
        logging.info("震荡区间不满足")
        return False, None, None
    # 2. 高点和低点之间存在3个点以上差距小于1/2*当下级别ATR的300SMA
    # atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=200)
    atr = calculate_atr(df, period=200)
    atr_half = atr.iloc[-1] / 2
    logging.info(f"1/2 atr {atr.iloc[-1]/2}")

    highs = [item for item in extrema if item['type'] == 'high']
    lows = [item for item in extrema if item['type'] == 'low']
    high_lines, key_high_points = is_difference_less_than_threshold(highs[-12:], threshold = atr_half)
    low_lines, key_low_points = is_difference_less_than_threshold(lows[-12:], threshold = atr_half)


    if high_lines.__len__() == 0 and low_lines.__len__() == 0:
        logging.info("关键位置不满足")
        return False, None, None

    # 3. 当前价离最近一条关键位置超过2%的不看
    current_price = df['close'].iloc[-1]
    nearest_high_line = None
    nearest_high_points = []
    nearest_low_line = None
    nearest_low_points = []
    if high_lines.__len__() > 0:
        nearest_high_line = high_lines[0]
        for high_index, high_line in enumerate(high_lines):
            if abs(high_line - current_price) < abs(nearest_high_line - current_price):
                nearest_high_line = high_line
                nearest_high_points = key_high_points[high_index]

    if low_lines.__len__() > 0:
        nearest_low_line = low_lines[0]
        for low_index, low_line in enumerate(low_lines):
            if abs(low_line - current_price) < abs(nearest_low_line - current_price):
                nearest_low_line = low_line
                nearest_low_points = key_low_points[low_index]


    if nearest_high_line is not None:
        if abs(nearest_high_line - current_price) / current_price >= 0.01 and nearest_low_line is None:
            logging.info("最后价格不满足")
            return False, None, None
    if nearest_low_line is not None:
        if abs(nearest_low_line - current_price) / current_price >= 0.01 and nearest_high_line is None:
            logging.info("最后价格不满足")
            return False, None, None

    if nearest_high_line is not None and nearest_low_line is not None:
        if abs(nearest_high_line - current_price) / current_price >= 0.01 and abs(nearest_low_line - current_price) / current_price >= 0.01:
            logging.info("最后价格不满足")
            return False, None, None
        elif current_price > nearest_high_line and current_price < nearest_low_line:
            logging.info("最后价格不满足")
            return False, None, None

    # 4. 形成关键位置的三个点和当前价之间有更高的高点或者更低的地点超过关键位置4%
    if nearest_high_points.__len__() > 0:
        nearest_high_point = nearest_high_points[-1]
        high_values = df['high'].iloc[nearest_high_point['index']:]
        if abs(high_values.max() - nearest_high_point['price']) / nearest_high_point['price'] > 0.02:
            logging.info("中间价格高过关键位置")
            return False, None, None

    if nearest_low_points.__len__() > 0:
        nearest_low_point = nearest_low_points[-1]
        low_values = df['low'].iloc[nearest_low_point['index']:]
        if abs(low_values.min() - nearest_low_point['price']) / nearest_low_point['price'] > 0.02:
            logging.info("中间价格低过关键位置")
            return False, None, None
    return True, nearest_high_line, nearest_low_line