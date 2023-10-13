from service import symbols

def calculate(args):
  symbol = args['symbol']
  symbol_type = args['symbol_type']
  entry_price = args['entry_price']
  sl_price = args['sl_price']
  tp_price = args['tp_price']
  risk_amount = args['risk_amount']
  margin_level = args['margin_level']

  units_per_lot = symbols.get_symbol_units_per_lot(symbol)


  if symbol_type == 'cn_goods':
    ac_slash_pc = 1
    account_currency = 'CNY'
  elif symbol_type == 'currency':

    margin_currency = symbol[:3]
    profit_currency = symbol[3:]

    account_currency = 'USD'

    ac_slash_pc = symbols.get_latest_currency_price(f'{account_currency}{profit_currency}')
    mc_slash_ac = symbols.get_latest_currency_price(f'{margin_currency}{account_currency}')
    print(f'{account_currency}{profit_currency}', ac_slash_pc)
    print(f'{account_currency}{margin_currency}', mc_slash_ac)

  # risk_amount 以 account_currency 为单位，要转成pc
  sl = abs(sl_price - entry_price)
  tp = abs(tp_price - entry_price)






  units = round( risk_amount * ac_slash_pc / sl, 2)

  # units_value 持仓价值是持仓units数量的保证金货币的价值，需要把mc转成ac计算保证金
  if symbol_type == 'cn_goods':
    units_value = units * entry_price
  elif symbol_type == 'currency':
    units_value = units * mc_slash_ac

  margin = round(units_value * margin_level, 2)

  lots = round(units / units_per_lot, 2)

  risk_reward_ratio = round(tp / sl, 2)


  return {
    'lots': lots,
    'margin': f'{margin} {account_currency}',
    'risk_reward_ratio': risk_reward_ratio,
    'units': units,
    'units_value': f'{round(units_value, 2)} {account_currency}',
  }