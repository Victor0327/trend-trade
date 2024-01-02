from datetime import datetime

from utils.date import unix_ms_timestamp_to_date_string

from indicator.zigzag import zigzag_indicator
from strategy.standard import is_need_to_alert
from table.strategy_opportunities import post_sql, get_last_oppo_sql, update_breakout_high_price, update_breakout_low_price
from service.postgres_engine import post_db
from service.email import send_email


def oppo_standard_breakout_strategy(df, symbol, symbol_type,
                                    interval, strategy_name,
                                    startTime, endTime):

  extrema = zigzag_indicator(df, ext_depth=8, ext_backstep=2)
  period = 90
  points = 6
  is_need, nearest_high_line, nearest_low_line =  is_need_to_alert(df, extrema, period, points)
  last_oppo = post_db.run_sql_to_dict_list(get_last_oppo_sql({
     'symbol': symbol,
     'strategy_name': strategy_name
  }))

  last_oppo = last_oppo[0] if last_oppo.__len__() > 0 else None

  current_close_price = df.iloc[-1]['close']
  current_high_price = df.iloc[-1]['high']
  current_low_price = df.iloc[-1]['low']
  current_close_price_time = df.index[-1]

  # 1. 如果还没创建过数据，且产生新的机会，则报警，记录机会。
  if last_oppo is None and is_need is True and (nearest_high_line is not None or nearest_low_line is not None):
    sql = post_sql({
      'symbol': symbol,
      'symbol_type': symbol_type,
      'interval': interval,
      'start_time': unix_ms_timestamp_to_date_string(startTime),
      'end_time': unix_ms_timestamp_to_date_string(endTime),
      'nearest_high_line': nearest_high_line if nearest_high_line else 'NULL',
      'nearest_low_line': nearest_low_line if nearest_low_line else 'NULL',
      'strategy_name': strategy_name,
      'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    post_db.run_sql_to_commit(sql)
    send_email(f"【{symbol}进入盘整】阻力{nearest_high_line} 支撑{nearest_low_line}", f"时间{current_close_price_time}", "513909280@qq.com")

  if nearest_low_line and current_high_price > nearest_low_line and current_close_price < nearest_low_line:
    post_db.run_sql_to_commit(update_breakout_low_price({
      'id': last_oppo['id'],
      'breakout_low_line_price': current_close_price,
      'breakout_low_line_time': current_close_price_time
    }))
    send_email(f"【{symbol}价格穿过支撑】{current_close_price} 穿过 {nearest_low_line}", f"时间{current_close_price_time}", "513909280@qq.com")

  elif nearest_high_line and current_low_price < nearest_high_line and current_close_price > nearest_high_line:
    post_db.run_sql_to_commit(update_breakout_high_price({
      'id': last_oppo['id'],
      'breakout_high_line_price': current_close_price,
      'breakout_high_line_time': current_close_price_time
    }))
    send_email(f"【{symbol}价格穿过阻力】{current_close_price} 穿过 {nearest_high_line}", f"时间{current_close_price_time}", "513909280@qq.com")

  elif last_oppo and (
     (nearest_low_line and last_oppo['nearest_low_line'] and str(round(nearest_low_line,5)) != str(round(last_oppo['nearest_low_line'],5)))
     or (nearest_high_line and last_oppo['nearest_high_line'] and str(round(nearest_high_line,5)) != str(round(last_oppo['nearest_high_line'],5)))
     ) and is_need is True:
    sql = post_sql({
      'symbol': symbol,
      'symbol_type': symbol_type,
      'interval': interval,
      'start_time': unix_ms_timestamp_to_date_string(startTime),
      'end_time': unix_ms_timestamp_to_date_string(endTime),
      'nearest_high_line': nearest_high_line if nearest_high_line else 'NULL',
      'nearest_low_line': nearest_low_line if nearest_low_line else 'NULL',
      'strategy_name': strategy_name,
      'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    post_db.run_sql_to_commit(sql)
