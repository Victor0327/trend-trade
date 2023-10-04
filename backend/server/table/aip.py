def get_aip_list_sql():
    return f"""
    select
    *
    from automatic_investment_plan
    where delete_flag is false;
"""

def get_symbol_today_price_sql(today_price_args):
    return f"""
    select
    close
    from {today_price_args['table_name']}
    where start_time = '{today_price_args['start_time']}';
"""

def get_symbol_close_price_list_sql(args):
    return f"""
    select
    close
    from {args['table_name']}
    where 1 = 1
    and start_time between '{args['start_time']}' and '{args['end_time']}'
    ;
"""