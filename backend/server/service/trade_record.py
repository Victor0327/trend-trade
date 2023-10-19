import pandas as pd
from service.postgres_engine import post_db as postgres_engine
import table.trade_record.record as t_trade_record


# 使用groupby进行分组，并对每组应用自定义函数
def aggregate_rows(g):
    tuples = list(zip(g['strategy_requirement_title'], g['strategy_requirement_performance']))
    # 使用第一行为基础创建新行
    first_row = g.iloc[0].copy()
    first_row['strategy_requirement_performance_array'] = [t for t in tuples if t[0] is not None]
    return first_row

def get_trade_record_df(args):
  sql = t_trade_record.get_data_sql(args)
  result_df = postgres_engine.run_sql_to_df(sql)
  result_df = result_df.fillna('')

  result_df = result_df.groupby(['id', 'open_date', 'symbol_type', 'symbol', 'risk', 'result', 'strategy_name']).apply(aggregate_rows).reset_index(drop=True)
  result_df = result_df.drop(columns=['strategy_requirement_title', 'strategy_requirement_performance'])
  return result_df

def get_cumulative_sum(args):
  result_df = get_trade_record_df(args)
  result_df = result_df[result_df['result'] != '']
  result_df = result_df[['open_date','result']].sort_values(by='open_date')
  result_df['cumulative_result'] = result_df['result'].cumsum()
  print(result_df)
  return result_df.to_dict(orient='records')


def get_trade_record(args):
  result_df = get_trade_record_df(args).sort_values(by='open_date', ascending=False)
  print(result_df)
  return result_df.to_dict(orient='records')

def create_trade_record(args):
  sql = t_trade_record.create_data_sql(args)
  print(sql)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'

def close_position(args):
  sql = t_trade_record.close_position_sql(args)
  print(sql)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'

def delete_trade_record(args):
  sql = t_trade_record.delete_data_sql(args)
  print(sql)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'

def get_strategy():
  sql = t_trade_record.get_strategy()
  return postgres_engine.run_sql_to_dict_list(sql)

def get_strategy_requirement(args):
  sql = t_trade_record.get_strategy_requirement(args)
  return postgres_engine.run_sql_to_dict_list(sql)
