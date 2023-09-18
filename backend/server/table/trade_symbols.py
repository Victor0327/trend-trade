def get_list_sql(args):
    return f"""
    select
    id,
    symbol,
    type,
    symbol_title
    from trade_symbols
    where active_flag is true;
"""
