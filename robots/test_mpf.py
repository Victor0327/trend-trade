import mplfinance as mpf
import pandas as pd
import numpy as np
from index import xrp_bars
# 随机生成一些数据



# 生成日期索引
index = pd.date_range(start='2020-01-01', periods=30)

# 创建 DataFrame

# 挑选一些点来进行标记
highlight = xrp_bars.index[(xrp_bars['High'] > 0.7) & (xrp_bars['High'] < 0.71)]

# 创建用于高亮显示的 DataFrame
highlight_df = pd.DataFrame(xrp_bars.loc[highlight])

# 创建 addplot 对象
ap = mpf.make_addplot(highlight_df, scatter=True, markersize=100, marker='o', color='r')

# 绘制图形
mpf.plot(xrp_bars, type='line', addplot=ap)
