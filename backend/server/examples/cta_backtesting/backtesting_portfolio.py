import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

package_path = os.path.dirname(os.path.dirname(script_dir))

sys.path.append(package_path)

print(package_path)
from vnpy_ctastrategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy_ctastrategy.strategies.standard_consolidation_breakout import StandardConsolidationBreakoutStrategy
from datetime import datetime

def run_backtesting(strategy_class, setting, vt_symbol, interval, start, end, rate, slippage, size, pricetick, capital, risk_free, annual_days):
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=interval,
        start=start,
        end=end,
        rate=rate,
        slippage=slippage,
        size=size,
        pricetick=pricetick,
        capital=capital,
        risk_free=risk_free,
        annual_days=annual_days
    )
    engine.add_strategy(strategy_class, setting)
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    return df

def show_portafolio(df):
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="portfolio.BINANCE",
        interval="1m",
        start=None,
        rate=0,
        slippage=0,
        size=1,
        pricetick=0,
        capital=150_000,
        # 无风险利率
        risk_free=0.024,
        # 年化交易日数量
        annual_days=365
    )
    statistics = engine.calculate_statistics(df)
    engine.show_chart(df, statistics)

df1 = run_backtesting(
    strategy_class=StandardConsolidationBreakoutStrategy,
    setting={},
    vt_symbol="BTCUSDT.BINANCE",
    interval="1m",
    start=datetime(2017, 8, 18),
    end=datetime(2023, 12, 1),
    rate=0.5/100000,
    slippage=1,
    size=1,
    pricetick=0.01,
    capital=50_000,
    # 无风险利率
    risk_free=0.024,
    # 年化交易日数量
    annual_days=365
    )

df2 = run_backtesting(
    strategy_class=StandardConsolidationBreakoutStrategy,
    setting={},
    vt_symbol="ETHUSDT.BINANCE",
    interval="1m",
    start=datetime(2017, 8, 18),
    end=datetime(2023, 12, 1),
    rate=0.5/100000,
    slippage=0.5,
    size=1,
    pricetick=0.01,
    capital=50_000,
    # 无风险利率
    risk_free=0.024,
    # 年化交易日数量
    annual_days=365
    )

df3 = run_backtesting(
    strategy_class=StandardConsolidationBreakoutStrategy,
    setting={},
    vt_symbol="LINKUSDT.BINANCE",
    interval="1m",
    start=datetime(2019, 2, 1),
    end=datetime(2023, 12, 1),
    rate=0.5/100000,
    slippage=0.01,
    size=1,
    pricetick=0.01,
    capital=50_000,
    # 无风险利率
    risk_free=0.024,
    # 年化交易日数量
    annual_days=365
    )

dfp = df1 + df2 + df3
dfp =dfp.dropna()
show_portafolio(dfp)