import pandas as pd
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
