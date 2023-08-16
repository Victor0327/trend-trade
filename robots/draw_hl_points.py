import os
from datetime import datetime
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from zigzag import zigzag_indicator
from strategy import is_need_to_alert

def draw_hl_points(tuple):
    df, title, type = tuple
    # 计算zigzag指标，并得到极值点的位置
    extrema = zigzag_indicator(df, ext_depth=8, ext_backstep=2)

    is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema)
    if is_need is not True:
        print("no need", title)
        return False
    # 国内股票不能做空
    if type == 'domestic_stock' and nearest_high_line is None:
        print("no need", title)
        return False
    # 高点和低点的index和price
    high_points = [(point['index'], point['price']) for point in extrema if point['type'] == 'high']
    low_points = [(point['index'], point['price']) for point in extrema if point['type'] == 'low']

    # 高点和低点的index
    high_indexes = [idx for idx, price in high_points]
    low_indexes = [idx for idx, price in low_points]

    # 高点和低点的价格
    high_prices = [price for idx, price in high_points]
    low_prices = [price for idx, price in low_points]

    # 使用df的索引创建一个新的pandas Series，并使用NaN填充
    high_prices_series = pd.Series(np.full(len(df), np.nan), index=df.index)
    low_prices_series = pd.Series(np.full(len(df), np.nan), index=df.index)

    # 更新高点和低点的价格
    high_prices_series.loc[df.index[high_indexes]] = high_prices
    low_prices_series.loc[df.index[low_indexes]] = low_prices

    # 使用新创建的Series创建addplot对象
    apds = [mpf.make_addplot(high_prices_series, scatter=True, type='line', color='r', linewidths=1.5, marker='o', markersize=10),
            mpf.make_addplot(low_prices_series, scatter=True, type='line', color='g', linewidths=1.5, marker='o', markersize=10)]

    if nearest_high_line is not None:
        apds.append(mpf.make_addplot([nearest_high_line] * len(df), scatter=True,  type='line', color='r'))

    if nearest_low_line is not None:
        apds.append(mpf.make_addplot([nearest_low_line] * len(df), scatter=True,  type='line', color='g'))


    date = datetime.now().strftime("%Y-%m-%d")
    # hour_date = datetime.now().strftime("%Y-%m-%d-%H")
    # project_root = dirname(dirname(__file__))
    project_root = "/tmp/"
    chart_save_dir = os.path.join(project_root, f"{date}_chart", type)
    # print(chart_save_dir)
    if not os.path.exists(chart_save_dir):
        os.makedirs(chart_save_dir)

    chart_save_path = os.path.join(chart_save_dir, f"{title}.png")
    mpf.plot(df, type='candle', addplot=apds, style='starsandstripes', title=title, savefig=dict(fname=chart_save_path, dpi=300, facecolor='w', pad_inches=0.25))
