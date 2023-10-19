from service import trade_record


def get_trade_record(args):
  return trade_record.get_trade_record(args)

def create_trade_record(args):
  return trade_record.create_trade_record(args)

def close_position(args):
  return trade_record.close_position(args)

def delete_trade_record(args):
  return trade_record.delete_trade_record(args)

def get_cumulative_sum(args):
  return trade_record.get_cumulative_sum(args)

def get_strategy():
  return trade_record.get_strategy()

def get_strategy_requirement(args):
  return trade_record.get_strategy_requirement(args)