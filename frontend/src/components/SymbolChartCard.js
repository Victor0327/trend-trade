import React, { useState, useEffect, useRef } from 'react';
import { Card, Radio, Flex, Button, message } from 'antd';
import { createChart } from 'lightweight-charts';
import { convert_list_data_to_lightweight_charts_format } from '../utils/transferModel'

import { commonService } from '../services/CommonService'



const App = (props) => {
  var seriesesData = new Map();

  const { symbol, type, symbolTitle } = props;
  console.log(symbol, type)

  var intervals = undefined

  if (type === 'crypto') {
    intervals = ['15m', '1d']
  } else if (type === 'cn_goods') {
    intervals = ['15', '1d', '1']
  } else {
    intervals = ['15', '1d']
  }

  const chartRef = useRef(null);
  const candlestickSeries = useRef(null);

  const syncToInterval = (interval) => {
    if (candlestickSeries.current && chartRef.current) {
      chartRef.current.removeSeries(candlestickSeries.current);
      candlestickSeries.current = null;
    }
    candlestickSeries.current = chartRef.current.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      priceFormat: {
          type: 'price',
          precision: type === 'currency' ? 5 : 2,
          minMove: 0.00001,
      },
    });
    candlestickSeries.current.setData(seriesesData.get(interval));
  }

  const fetchData = (symbol_type, symbol, interval, page, limit) => {
    return commonService.get(`/symbol_data?symbol_type=${symbol_type}&symbol=${symbol}&interval=${interval}&page=${page}&limit=${limit}`).then((res) => {
      return convert_list_data_to_lightweight_charts_format(res.data.data)
    })
  }

  const handleChangeSwitcher = (e) => {
    const interval = e.target.value
    syncToInterval(interval)
  }

  const renderChart = () => {
      const chartContainer = document.getElementById(props.symbol);

      chartRef.current = createChart(chartContainer, {
        // width: 390,
        // height: 280,
        layout: {
          background: {
                  type: 'solid',
                  color: '#000000',
              },
          textColor: '#d1d4dc',
        },
        grid: {
          vertLines: {
            visible: false,
          },
          horzLines: {
            color: 'rgba(42, 46, 57, 0.5)',
          },
        },
        rightPriceScale: {
          borderVisible: false,
        },
        timeScale: {
          borderVisible: false,
        },
        crosshair: {
          horzLine: {
            visible: false,
          },
        },
      });
      chartRef.current.timeScale().fitContent();

  }

  useEffect(() => {

    const promiseArray = intervals.map((interval) => fetchData(type, symbol, interval, 1, 1000))

    Promise.all(promiseArray).then((dataArray) => {
      dataArray.forEach((data, index) => {
        seriesesData.set(intervals[index], data)
      })
      renderChart()
      syncToInterval(intervals[0])
    })
  }, []); // 注意这里的空依赖数组

  return (
    <Card title={symbolTitle}
      style={{
        marginBottom: 10
      }}
    >
      <div id={props.symbol} style={{ width: '100%', height: '280px' }}></div>
      <Flex
          style={{
            width: '100%',
            height: 40,
          }}
          justify="space-between"
          align="flex-end"
      >
      <Radio.Group
        defaultValue={intervals[0]} buttonStyle="solid" onChange={handleChangeSwitcher}
      >
        {
          intervals.map((interval, index) => {
            return <Radio.Button key={index} value={interval}>{interval}</Radio.Button>
          })
        }
      </Radio.Group>
      <Button type="default"
        onClick={props.onPinToTop}
      >置顶</Button>
      </Flex>
    </Card>
  )
};
export default App;