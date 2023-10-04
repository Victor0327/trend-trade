from utils.date import unix_ms_timestamp_to_date_string

def get_insert_sql(params, data_list):

    value_str = 'VALUES '
    for data in data_list:
        value_str = value_str + f"('{unix_ms_timestamp_to_date_string(data[0])}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}', '{data[5]}', '{unix_ms_timestamp_to_date_string(data[6])}','{data[7]}','{data[8]}','{data[9]}','{data[10]}'),"

    value_str = value_str[0:-1]

    return f"""
      INSERT INTO crypto_{params['pair']}_{params['contractType']}_{params['interval']} (
        start_time,
        open,
        high,
        low,
        close,
        volume,
        end_time,
        volume_money,
        volume_orders,
        active_buy_volume,
        active_buy_volume_money
        )
      {value_str}
      on conflict(start_time)
      do update set (
        open,
        high,
        low,
        close,
        volume,
        end_time,
        volume_money,
        volume_orders,
        active_buy_volume,
        active_buy_volume_money
      ) = (
        excluded.open,
        excluded.high,
        excluded.low,
        excluded.close,
        excluded.volume,
        excluded.end_time,
        excluded.volume_money,
        excluded.volume_orders,
        excluded.active_buy_volume,
        excluded.active_buy_volume_money
      );
    """