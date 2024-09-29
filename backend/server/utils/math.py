import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP


def calculate_atr(df, period=14):
    # 计算三个可能的真实范围值
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()

    # 真实范围是三者中的最大值
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # ATR是真实范围的移动平均
    atr = tr.rolling(window=period).mean()

    return atr

def average(decimal_list):
    # 判断列表是否为空
    if not decimal_list:
        return None
    # 计算总和
    total = sum(decimal_list)
    # 计算平均数
    return total / Decimal(len(decimal_list))

def round_decimal(d: Decimal, places='0.01'):
    return d.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def slice_top_elements_from_np_array(array: np.array, is_highest: bool, n_top: int = 3):

    # 使用分区去掉最高的n个数，此操作不会排序整个数组
    if is_highest:
        partitioned_array = np.partition(array, -n_top)
        sliced_values = partitioned_array[-n_top:]  # 被切掉的最高的n个数
        trimmed_array = partitioned_array[:-n_top]  # 去掉最高n个数后的数组
    else:
        partitioned_array = np.partition(array, n_top)
        sliced_values = partitioned_array[:n_top]  # 被切掉的最高的n个数
        trimmed_array = partitioned_array[n_top:]  # 去掉最高n个数后的数组

    return trimmed_array, sliced_values
