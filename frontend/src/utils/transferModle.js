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

export {
  transferOpsList,
  convert_list_data_to_lightweight_charts_format
}