import pandas as pd
from enum import Enum

class ZigZagType(Enum):
    HH = "HH"  # Higher High
    HL = "HL"  # Higher Low
    LL = "LL"  # Lower Low
    LH = "LH"  # Lower High

def zigzag_indicator(df, pips = 0.01, ext_depth = 12, ext_deviation = 0, ext_backstep = 3):
    high_list = df['High'].tolist()
    low_list = df['Low'].tolist()
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
                extrema.append({"index": last_lowest_index, "price": low_list[last_lowest_index], "type": last_extrema_type})
            last_extrema_type = "high"
        elif low_list[i] < last_lowest - ext_deviation * pips:
            last_lowest = low_list[i]
            last_lowest_index = i
            if last_extrema_type == "high":
                extrema.append({"index": last_highest_index, "price": high_list[last_highest_index], "type": last_extrema_type})
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
        extrema.append({"index": last_highest_index, "price": high_list[last_highest_index], "type": last_extrema_type})
    elif last_extrema_type == "low":
        extrema.append({"index": last_lowest_index, "price": low_list[last_lowest_index], "type": last_extrema_type})

    return extrema
