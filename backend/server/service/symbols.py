from service.postgres_engine import post_db as postgres_engine
import table.symbol.t_symbols as t_symbols
import table.symbol.my_focus as my_focus





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


def get_my_focus_symbols(args):
  sql = my_focus.get_list_sql(args)
  count_sql = my_focus.get_list_count_sql(args)
  list = postgres_engine.run_sql_to_dict_list(sql)
  count = postgres_engine.run_sql_to_dict_list(count_sql)

  return list, count[0]['count']

def pin_to_top(args):
  sql = my_focus.pin_to_top(args)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'

def add_to_focus(args):
  sql = my_focus.add_to_focus(args)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'

def remove_from_focus(args):
  sql = my_focus.remove_from_focus(args)
  postgres_engine.run_sql_to_commit(sql)

  return 'success'