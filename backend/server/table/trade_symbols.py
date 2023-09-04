def get_list_sql(args):
    return f"""
    select
    *
    from trade_symbols
    where active_flag is true;
"""
