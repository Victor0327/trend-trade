def get_list_sql(args):
    return f"""
    select
    *
    from trade_symbols
    where active_flag is true;
"""

def post_sql(args):
    return f"""
    INSERT INTO "public"."trade_opportunities"("create_date","symbol","interval","period","type","title")
    VALUES
    (CURRENT_DATE, '{args['symbol']}','{args['interval']}','{args['period']}','{args['type']}','{args['title']}')
    ON CONFLICT ("create_date", "symbol")
    DO UPDATE SET
    "interval" = EXCLUDED."interval",
    "period" = EXCLUDED."period",
    "type" = EXCLUDED."type",
    "title" = EXCLUDED."title";

"""

def get_list_by_create_date_sql(args):
    args['page'] = 1 if 'page' not in args else args['page']
    args['limit'] = 10 if 'limit' not in args else args['limit']
    return f"""
    select
    symbol,
    interval,
    period
    from trade_opportunities
    where active_flag is true
    and create_date = '{args['create_date']}'
    OFFSET ({args['page']} - 1) * {args['limit']}
    LIMIT {args['limit']};
"""

def get_list_by_create_date_count_sql(args):
    return f"""
    select
    count(*)
    from trade_opportunities
    where active_flag is true
    and create_date = '{args['create_date']}';
"""
