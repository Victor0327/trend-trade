from service.postgres_engine import post_db as postgres_engine
import table.symbol.t_symbol_data as t_symbol_data





def get_symbol_data(args):
  sql = t_symbol_data.get_data_sql(args)
  data = postgres_engine.run_sql_to_tuple_list(sql)
  data_for_chart = data[::-1]

  return data_for_chart
