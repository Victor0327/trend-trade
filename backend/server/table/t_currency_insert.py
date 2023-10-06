def create_table_and_index_sql(params):
    return f"""
CREATE TABLE IF NOT EXISTS currency_{params['symbol']}_{params['interval']} (
    id SERIAL PRIMARY KEY,
    date timestamp(6) without time zone UNIQUE,
    open numeric(10,3),
    high numeric(10,3),
    low numeric(10,3),
    close numeric(10,3)
);


CREATE UNIQUE INDEX IF NOT EXISTS currency_{params['symbol']}_{params['interval']}_pkey ON currency_{params['symbol']}_{params['interval']}(id int4_ops);
CREATE UNIQUE INDEX IF NOT EXISTS currency_{params['symbol']}_{params['interval']}_date_key ON currency_{params['symbol']}_{params['interval']}(date timestamp_ops);

    """

def get_insert_sql(params, data_list):

    value_str = 'VALUES '
    for data in data_list:
        if 'd' in data:
          value_str = value_str + f"('{data['d']}', '{data['o']}', '{data['h']}', '{data['l']}', '{data['c']}'),"
        else :
          # 先低再高
          value_str = value_str + f"('{data[0]}', '{data[1]}', '{data[3]}', '{data[2]}', '{data[4]}'),"

    value_str = value_str[0:-1]

    return f"""
      INSERT INTO currency_{params['symbol']}_{params['interval']} (
        date,
        open,
        high,
        low,
        close
        )
      {value_str}
      on conflict(date)
      do update set (
        open,
        high,
        low,
        close
      ) = (
        excluded.open,
        excluded.high,
        excluded.low,
        excluded.close
      );
    """