def get_data_sql(args):
    symbol_type = args['symbol_type']
    symbol = args['symbol']
    interval = args['interval']
    table_name = f"{symbol_type}_{symbol}_{interval}"
    page = args['page'] if args['page'] else 1
    limit = args['limit'] if args['limit'] else 1000
    if symbol_type == 'crypto':
        date = 'start_time'
    else:
        date = 'date'
    return f"""
    select
      EXTRACT(EPOCH FROM {date}),
      open,
      high,
      low,
      close
    from {table_name}
    order by {date} desc
    OFFSET ({page} - 1) * {limit}
    LIMIT {limit};
"""

def get_raw_data_sql(args):
    symbol_type = args['symbol_type']
    symbol = args['symbol']
    interval = args['interval']
    table_name = f"{symbol_type}_{symbol}_{interval}"
    page = args['page'] if args['page'] else 1
    limit = args['limit'] if args['limit'] else 1000
    if symbol_type == 'crypto':
        date = 'start_time'
    else:
        date = 'date'
    return f"""
    select
      EXTRACT(EPOCH FROM {date} AT TIME ZONE 'Asia/Shanghai' AT TIME ZONE 'UTC'),
      open,
      high,
      low,
      close,
      volume,
      position
    from {table_name}
    order by {date} desc
    OFFSET ({page} - 1) * {limit}
    LIMIT {limit};
"""

def get_symbol_data_count(args):
    symbol_type = args['symbol_type']
    symbol = args['symbol']
    interval = args['interval']
    table_name = f"{symbol_type}_{symbol}_{interval}"

    return f"""
    select count(*) from {table_name};
"""
