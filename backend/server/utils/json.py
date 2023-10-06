from datetime import datetime
from decimal import Decimal

def custom_json_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)  # 或者 float(obj) 根据需要
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")