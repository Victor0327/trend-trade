const transferOpsList = (dataList) => {

  return dataList.map((item) => {

    return {
      symbol: item['symbol'],
      interval: item['interval'],
      period: item['period'],
    }
  })
}

const convert_list_data_to_lightweight_charts_format = (data) => {
    return data.map((item) => {
      return {
        "time": item[0],
        "open": item[1],
        "high": item[2],
        "low": item[3],
        "close": item[4]
      }
    })
}

const calculate_descriptions_map = {
  'lots': '开仓手数',
  'margin': '所需保证金',
  'risk_reward_ratio': '盈亏比',
  'units': '实际仓位',
  'units_value': '实际仓位价值',
}

export {
  transferOpsList,
  convert_list_data_to_lightweight_charts_format,
  calculate_descriptions_map
}