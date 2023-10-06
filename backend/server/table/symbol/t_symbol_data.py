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