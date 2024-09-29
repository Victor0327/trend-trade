import pandas as pd
from enum import Enum

# Re-importing pandas as the execution environment has been reset.
import pandas as pd

def calculate_zigzag_indicator(
        high_list,
        low_list,
        # 深度，极值点的计算窗口。高点为最近多少根K线产生的高点。低点为最近多少根K线产生的低点。
        depth = 7,
        # 偏差，新的低点比上一个低点高了多少个点，就不算低点。新的高点比上一个高点低了多少点就不算高点。
        deviation = 0,
        # 回溯，一旦有新的低点，把最近多少根K线产生的低点都去掉。一旦有新的高点，把最近多少根K线产生的高点都去掉。
        backstep = 3):

    len_price = len(high_list)
    extrema = []
    if high_list.__len__() < depth:
        return extrema
    last_highest = high_list[depth]
    last_lowest = low_list[depth]
    last_highest_index = depth
    last_lowest_index = depth
    last_extrema_type = None  # "high" or "low"
    i = depth
    while i < len_price:
        last_highest = max(high_list[i-depth:i]) # updating highest in ext_depth window
        last_lowest = min(low_list[i-depth:i]) # updating lowest in ext_depth window
        if high_list[i] > last_highest + deviation:
            last_highest = high_list[i]
            last_highest_index = i
            if last_extrema_type == "low":
                extrema.append({
                    "index": last_lowest_index,
                    "price": low_list[last_lowest_index],
                    "type": last_extrema_type,
                })
            last_extrema_type = "high"
        elif low_list[i] < last_lowest - deviation:
            last_lowest = low_list[i]
            last_lowest_index = i
            if last_extrema_type == "high":
                extrema.append({
                    "index": last_highest_index,
                    "price": high_list[last_highest_index],
                    "type": last_extrema_type,
                })
            last_extrema_type = "low"
        else:
            if high_list[i] > last_highest:
                last_highest = high_list[i]
                last_highest_index = i
            if low_list[i] < last_lowest:
                last_lowest = low_list[i]
                last_lowest_index = i

        if last_extrema_type == "high" and low_list[i] < last_highest - deviation:
            last_lowest = low_list[i]
            last_lowest_index = i
            i = i - backstep if i - backstep > last_lowest_index else last_lowest_index
        elif last_extrema_type == "low" and high_list[i] > last_lowest + deviation:
            last_highest = high_list[i]
            last_highest_index = i
            i = i - backstep if i - backstep > last_highest_index else last_highest_index

        i += 1

    if last_extrema_type == "high":
        extrema.append({
            "index": last_highest_index,
            "price": high_list[last_highest_index],
            "type": last_extrema_type,
        })
    elif last_extrema_type == "low":
        extrema.append({
            "index": last_lowest_index,
            "price": low_list[last_lowest_index],
            "type": last_extrema_type,
        })

    return extrema



def zigzag_indicator(df, pips = 0.01, ext_depth = 12, ext_deviation = 0, ext_backstep = 3):
    high_list = df['high'].tolist()
    low_list = df['low'].tolist()
    date_list = df.index.tolist()
    len_price = len(high_list)
    extrema = []
    if high_list.__len__() < ext_depth:
        return extrema
    last_highest = high_list[ext_depth]
    last_lowest = low_list[ext_depth]
    last_highest_index = ext_depth
    last_lowest_index = ext_depth
    last_extrema_type = None  # "high" or "low"
    i = ext_depth
    while i < len_price:
        last_highest = max(high_list[i-ext_depth:i]) # updating highest in ext_depth window
        last_lowest = min(low_list[i-ext_depth:i]) # updating lowest in ext_depth window
        if high_list[i] > last_highest + ext_deviation * pips:
            last_highest = high_list[i]
            last_highest_index = i
            if last_extrema_type == "low":
                extrema.append({
                    "index": last_lowest_index,
                    "price": low_list[last_lowest_index],
                    "type": last_extrema_type,
                    "date": date_list[last_lowest_index]
                })
            last_extrema_type = "high"
        elif low_list[i] < last_lowest - ext_deviation * pips:
            last_lowest = low_list[i]
            last_lowest_index = i
            if last_extrema_type == "high":
                extrema.append({
                    "index": last_highest_index,
                    "price": high_list[last_highest_index],
                    "type": last_extrema_type,
                    "date": date_list[last_highest_index]
                })
            last_extrema_type = "low"
        else:
            if high_list[i] > last_highest:
                last_highest = high_list[i]
                last_highest_index = i
            if low_list[i] < last_lowest:
                last_lowest = low_list[i]
                last_lowest_index = i

        if last_extrema_type == "high" and low_list[i] < last_highest - ext_deviation * pips:
            last_lowest = low_list[i]
            last_lowest_index = i
            i = i - ext_backstep if i - ext_backstep > last_lowest_index else last_lowest_index
        elif last_extrema_type == "low" and high_list[i] > last_lowest + ext_deviation * pips:
            last_highest = high_list[i]
            last_highest_index = i
            i = i - ext_backstep if i - ext_backstep > last_highest_index else last_highest_index

        i += 1

    if last_extrema_type == "high":
        extrema.append({
            "index": last_highest_index,
            "price": high_list[last_highest_index],
            "type": last_extrema_type,
            "date": date_list[last_highest_index]
        })
    elif last_extrema_type == "low":
        extrema.append({
            "index": last_lowest_index,
            "price": low_list[last_lowest_index],
            "type": last_extrema_type,
            "date": date_list[last_lowest_index]
        })

    return extrema
