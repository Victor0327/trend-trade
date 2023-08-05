import pandas as pd

def calculate_atr(df, period=14):
    # 计算三个可能的真实范围值
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift(1)).abs()
    low_close = (df['Low'] - df['Close'].shift(1)).abs()

    # 真实范围是三者中的最大值
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # ATR是真实范围的移动平均
    atr = tr.rolling(window=period).mean()

    return atr