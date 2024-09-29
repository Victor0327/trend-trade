import sys
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录路径
script_dir = os.path.dirname(script_path)

package_path = os.path.dirname(os.path.dirname(script_dir))

sys.path.append(package_path)

print(package_path)

from datetime import datetime

from vnpy.trader.optimize import OptimizationSetting
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_ctastrategy.strategies.standard_breakout import StandardBreakoutStrategy
from vnpy_ctastrategy.strategies.standard_consolidation_breakout import StandardConsolidationBreakoutStrategy

engine = BacktestingEngine()
engine.set_parameters(
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
engine.add_strategy(StandardConsolidationBreakoutStrategy, {})

engine.load_data()
engine.run_backtesting()
df = engine.calculate_result()
statistics = engine.calculate_statistics()
engine.show_chart(statistics=statistics)

# 优化参数
# setting = OptimizationSetting()
# setting.set_target("sharpe_ratio")
# setting.add_parameter("atr_length", 25, 27, 1)
# setting.add_parameter("atr_ma_length", 10, 30, 10)

# engine.run_ga_optimization(setting)

# engine.run_bf_optimization(setting)