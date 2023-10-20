def get_list_sql(args):
    return f"""
    select
        symbols.id,
        symbol,
        type,
        symbol_title,
        my_focus_symbols.id as my_focus_symbols_id
    from symbols
    left join my_focus_symbols on symbols.id = my_focus_symbols.symbols_id
    where active_flag is true
    and type = '{args['type']}'
    order by id asc;
"""

def get_latest_currency_price(pair: str):
    return f"""
    select
        close
    from currency_{pair.lower()}_15
    order by date desc
    limit 1;
"""

def get_currency_symbols():
    return f"""
    select
        symbol
    from symbols
    where active_flag is true
        and type = 'currency';
"""

def get_symbol_units_per_lot(symbol):
    return f"""
    select
        units_per_lot
    from symbols
    where active_flag is true
        and symbol = '{symbol}';
"""