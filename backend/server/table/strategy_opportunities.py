def get_last_oppo_sql(args):
    return f"""
    select
        *
    from strategy_opportunities
    where symbol = '{args['symbol']}'
    and strategy_name = '{args['strategy_name']}'
    order by create_time desc
    limit 1;
    """


def update_breakout_high_price(args):
    return f"""
    update strategy_opportunities
    set
        breakout_high_line_price = {args['breakout_high_line_price']},
        breakout_high_line_time = '{args['breakout_high_line_time']}'
    where id = {args['id']};
    """

def update_breakout_low_price(args):
    return f"""
    update strategy_opportunities
    set
        breakout_low_line_price = {args['breakout_low_line_price']},
        breakout_low_line_time = '{args['breakout_low_line_time']}'
    where id = {args['id']};
    """


def post_sql(args):
    return f"""
    INSERT INTO "public"."strategy_opportunities"(
      "symbol",
      "symbol_type",
      "interval",
      "start_time",
      "end_time",
      "nearest_high_line",
      "nearest_low_line",
      "strategy_name",
      "create_time"
    )
    VALUES
    (
      '{args['symbol']}',
      '{args['symbol_type']}',
      '{args['interval']}',
      '{args['start_time']}',
      '{args['end_time']}',
      {args['nearest_high_line']},
      {args['nearest_low_line']},
      '{args['strategy_name']}',
      '{args['create_time']}'
    );

"""