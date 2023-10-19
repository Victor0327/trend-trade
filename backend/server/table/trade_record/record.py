def get_data_sql(args):
    risk_amount_currency = args['risk_amount_currency']
    risk_amount = args['risk_amount']
    table_name = f"risk_profit_history_{risk_amount_currency}_{risk_amount}"

    strategy_id = args['strategy_id'] if 'strategy_id' in args else None

    where_strategy_id_statement = f"and rh.strategy_id = {strategy_id}" if strategy_id is not None else ''

    return f"""
select
	rh.id,
	open_date,
	symbol_type,
	symbol,
	risk,
	result,
	s.name as strategy_name,
	sr.title as strategy_requirement_title,
	sh.performance as strategy_requirement_performance
from {table_name} rh
left join strategy s
	on s.id = rh.strategy_id
left join strategy_requirement_performance_history sh
	on sh.risk_profit_history_id = rh.id
	and sh.risk_amount = {risk_amount}
    and sh.risk_amount_currency = '{risk_amount_currency}'
left join strategy_requirement sr
	on sr.id = sh.strategy_requirement_id
where 1 = 1
{where_strategy_id_statement};
"""

def close_position_sql(args):
    risk_amount_currency = args['risk_amount_currency']
    risk_amount = args['risk_amount']
    table_name = f"risk_profit_history_{risk_amount_currency}_{risk_amount}"

    id = args['id']
    close_date = args['close_date']
    result = args['result']
    memo = args['memo']

    return f"""
    update {table_name}
    set
        close_date = '{close_date}',
        result = {result},
        memo = '{memo}'
    where id = {id};
    """

def delete_data_sql(args):
    risk_amount_currency = args['risk_amount_currency']
    risk_amount = args['risk_amount']
    table_name = f"risk_profit_history_{risk_amount_currency}_{risk_amount}"

    id = args['id']

    delete_risk_profit_history_sql = f"""
    delete from {table_name}
    where id = {id};
    """

    delete_strategy_requirement_performance_history_sql = f"""
    delete from strategy_requirement_performance_history
    where risk_profit_history_id = {id}
    and risk_amount = {risk_amount}
    and risk_amount_currency = '{risk_amount_currency}';
    """

    return f"""
    BEGIN;

    {delete_strategy_requirement_performance_history_sql}

    {delete_risk_profit_history_sql}

    COMMIT;
    """






def create_data_sql(args):
    risk_amount_currency = args['risk_amount_currency']
    risk_amount = args['risk_amount']
    table_name = f"risk_profit_history_{risk_amount_currency}_{risk_amount}"

    open_date = args['open_date']
    symbol_type = args['symbol_type']
    symbol = args['symbol']

    strategy_id = args['strategy_id']
    risk = args['risk']
    memo = args['memo']

    strategy_requirement_performance_array = args['strategy_requirement_performance_array']

    create_risk_profit_history_sql = f"""
    WITH ins AS (
      insert into {table_name} (
          open_date,
          symbol_type,
          symbol,
          risk,
          memo,
          strategy_id
      )
      values (
          '{open_date}',
          '{symbol_type}',
          '{symbol}',
          {risk},
          '{memo}',
          {strategy_id}
      )
      RETURNING id
    )
    """

    value_str = ''
    for data in strategy_requirement_performance_array:
        value_str = value_str + f"""
        select {args['risk_amount']}, '{args['risk_amount_currency']}', id, {data[0]}, '{data[1]}'
        from ins
        union all"""

    value_str = value_str[0:-9]



    strategy_requirement_performance_history_sql = f"""
        insert into strategy_requirement_performance_history (
            risk_amount,
            risk_amount_currency,
            risk_profit_history_id,
            strategy_requirement_id,
            performance
        )
        {value_str};
    """

    if value_str == '':
        return f"""
        BEGIN;

        {create_risk_profit_history_sql}

        select 1;
        COMMIT;
        """
    else:

        return f"""
        BEGIN;

        {create_risk_profit_history_sql}

        {strategy_requirement_performance_history_sql}

        COMMIT;
        """

def get_strategy():
    return f"""
    select
        id,
        name,
        abbr
    from strategy;
    """

def get_strategy_requirement(args):
    return f"""
    select
        id,
        title,
        memo
    from strategy_requirement
    where 1=1
    and strategy_id = {args['strategy_id']};
    """