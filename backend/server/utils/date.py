from datetime import datetime, timedelta
import pytz

def get_current_date(format='%Y-%m-%d %H:%M:%S'):
  # 获取当前日期
    current_date = datetime.now()

    date_string = current_date.strftime(format)
    return date_string

def get_delta_date(format='%Y-%m-%d %H:%M:%S', days=0, hours=0, minutes=0, seconds=0):
  # 获取当前日期
    date = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    date_string = date.strftime(format)
    return date_string

def unix_ms_timestamp_to_date_string(unix_ms_timestamp, format='%Y-%m-%d %H:%M:%S', timezone='Asia/Shanghai'):

    timestamp_milliseconds = unix_ms_timestamp
    timestamp_seconds = timestamp_milliseconds / 1000

    # 将时间戳转换为UTC的datetime对象
    dt_utc = datetime.fromtimestamp(timestamp_seconds, tz=pytz.utc)

    # 转换为北京时间
    beijing_tz = pytz.timezone(timezone)
    dt_beijing = dt_utc.astimezone(beijing_tz)

    # 格式化输出
    formatted_date_string = dt_beijing.strftime(format)
    return formatted_date_string


def date_string_to_unix_ms_timestamp(date_string, format='%Y-%m-%d %H:%M:%S', timezone='Asia/Shanghai'):
    dt = datetime.strptime(date_string, format)
    tz = pytz.timezone(timezone)
    dt = tz.localize(dt)
    unix_timestamp_milliseconds = int(dt.timestamp() * 1000)

    return unix_timestamp_milliseconds
