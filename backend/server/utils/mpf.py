import numpy as np
import pandas as pd
import mplfinance as mpf


def draw_k_lines(df, addplot, title='K lines'):

    # atr = calculate_atr(df, period=200)

    mpf.plot(df, type='candle', style='starsandstripes', title=title, addplot=addplot, volume=True)

