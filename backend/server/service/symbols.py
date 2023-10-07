from service.postgres_engine import post_db as postgres_engine
import table.symbol.t_symbols as t_symbols





def get_symbols(args):
  sql = t_symbols.get_list_sql(args)
  data = postgres_engine.run_sql_to_dict_list(sql)

  return data
