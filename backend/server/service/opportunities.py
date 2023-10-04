from service.postgres_engine import post_db as postgres_engine
from table.trade_opportunities import get_list_by_create_date_sql, get_list_by_create_date_count_sql





def get_opportunities_by_create_date(args):
  sql = get_list_by_create_date_sql(args)
  count_sql = get_list_by_create_date_count_sql(args)
  list = postgres_engine.run_sql_to_dict_list(sql)
  count = postgres_engine.run_sql_to_dict_list(count_sql)

  return list, count[0]['count']
