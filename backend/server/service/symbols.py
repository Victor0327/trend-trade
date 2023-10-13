from service.postgres_engine import post_db as postgres_engine
import table.symbol.t_symbols as t_symbols





def get_symbols(args):
  sql = t_symbols.get_list_sql(args)
  data = postgres_engine.run_sql_to_dict_list(sql)

  return data

def get_latest_currency_price(pair):
  reversed_pair = pair[3:] + pair[:3]
  currency_pairs = [t[0] for t in postgres_engine.run_sql_to_tuple_list(t_symbols.get_currency_symbols())]
  if pair in currency_pairs:
    sql = t_symbols.get_latest_currency_price(pair)
    data = postgres_engine.run_sql_to_tuple_list(sql)
    return float(data[0][0])
  elif reversed_pair in currency_pairs:
    sql = t_symbols.get_latest_currency_price(reversed_pair)
    data = postgres_engine.run_sql_to_tuple_list(sql)
    return 1 / float(data[0][0])
  elif pair == 'USDUSD':
    return 1


def get_symbol_units_per_lot(symbol):
  sql = t_symbols.get_symbol_units_per_lot(symbol)
  data = postgres_engine.run_sql_to_dict_list(sql)
  units_per_lot = data[0]['units_per_lot']

  return units_per_lot