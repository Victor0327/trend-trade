import pandas as pd
import logging
# import talib
from itertools import combinations
from utils.math import calculate_atr

def is_difference_less_than_threshold(prices, threshold):
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
    logging.info("1/2 atr", atr.iloc[-1]/2)

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