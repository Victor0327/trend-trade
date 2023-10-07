def get_list_sql(args):
    return f"""
    select
    id,
    symbol,
    type,
    symbol_title
    from symbols
    where active_flag is true
    and type = '{args['type']}';
"""
