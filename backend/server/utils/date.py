from datetime import datetime

def get_current_date():
  # 获取当前日期
    current_date = datetime.now().date()

    # 将日期转换为字符串格式
    date_string = current_date.strftime('%Y-%m-%d')
    return date_string