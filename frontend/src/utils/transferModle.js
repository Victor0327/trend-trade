const transferOpsList = (dataList) => {

  return dataList.map((item) => {

    return {
      symbol: item['symbol'],
      interval: item['interval'],
      period: item['period'],
    }
  })
}

export {
  transferOpsList
}