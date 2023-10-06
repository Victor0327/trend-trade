def create_table_and_index_sql(params):
    return f"""
CREATE TABLE IF NOT EXISTS cn_goods_{params['symbol']}_{params['interval']} (
    id SERIAL PRIMARY KEY,
    date timestamp(6) without time zone UNIQUE,
    open numeric(10,3),
    high numeric(10,3),
    low numeric(10,3),
    close numeric(10,3),
    volume bigint,
    position bigint
);


CREATE UNIQUE INDEX IF NOT EXISTS cn_goods_{params['symbol']}_{params['interval']}_pkey ON cn_goods_{params['symbol']}_{params['interval']}(id int4_ops);
CREATE UNIQUE INDEX IF NOT EXISTS cn_goods_{params['symbol']}_{params['interval']}_date_key ON cn_goods_{params['symbol']}_{params['interval']}(date timestamp_ops);

    """

def get_insert_sql(params, data_list):

    value_str = 'VALUES '
    for data in data_list:
        value_str = value_str + f"('{data['d']}', '{data['o']}', '{data['h']}', '{data['l']}', '{data['c']}', '{data['v']}', '{data['p']}'),"

    value_str = value_str[0:-1]

    return f"""
      INSERT INTO cn_goods_{params['symbol']}_{params['interval']} (
        date,
        open,
        high,
        low,
        close,
        volume,
        position
        )
      {value_str}
      on conflict(date)
      do update set (
        open,
        high,
        low,
        close,
        volume,
        position
      ) = (
        excluded.open,
        excluded.high,
        excluded.low,
        excluded.close,
        excluded.volume,
        excluded.position
      );
    """

# 删除数据
#     return f"""
# truncate table cn_goods_{params['symbol']}_{params['interval']} RESTART IDENTITY;
#     """