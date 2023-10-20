def get_list_sql(args):
    args['page'] = 1 if 'page' not in args else args['page']
    args['limit'] = 10 if 'limit' not in args else args['limit']
    return f"""
    select
      my_focus_symbols.id,
      symbols.symbol,
      symbols.type,
      symbols.symbol_title
    from my_focus_symbols
    inner join symbols on my_focus_symbols.symbols_id = symbols.id
                      and symbols.active_flag is true
                      and symbols.type = '{args['type']}'
    order by my_focus_symbols.update_time desc
    OFFSET ({args['page']} - 1) * {args['limit']}
    LIMIT {args['limit']};
"""

def get_list_count_sql(args):
    return f"""
    select
      count(*)
    from my_focus_symbols
    inner join symbols on my_focus_symbols.symbols_id = symbols.id
                      and symbols.active_flag is true
                      and symbols.type = '{args['type']}';
"""


def pin_to_top(args):
    return f"""
    update my_focus_symbols
    set update_time = now()
    where id = {args['id']};
"""

def add_to_focus(args):
    return f"""
    insert into my_focus_symbols (symbols_id, create_time, update_time)
    values ({args['id']}, now(), now());
"""

def remove_from_focus(args):
    return f"""
    delete from my_focus_symbols
    where id = {args['id']};
"""