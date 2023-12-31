import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Breadcrumb, theme, Radio, Space, Typography } from 'antd';
import { createChart } from 'lightweight-charts';

import { commonService } from '../services/CommonService'
import { convert_list_data_to_lightweight_charts_format } from '../utils/transferModel'
// import { seriesesData } from '../mock/chartData'


const { Title } = Typography;
var seriesesData = new Map();

const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const { symbol_type, symbol } = useParams();

  var intervals = undefined

  if (symbol_type === 'crypto') {
    intervals = ['15m', '1d']
  } else if (symbol_type === 'cn_goods') {
    intervals = ['1', '15', '1d']
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
      wickDownColor: '#ef5350'
    });
    candlestickSeries.current.setData(seriesesData.get(interval));
  }

  const fetchData = (symbol_type, symbol, interval, page, limit) => {
    return commonService.get(`/symbol_data?symbol_type=${symbol_type}&symbol=${symbol}&interval=${interval}&page=${page}&limit=${limit}`).then((res) => {
      return convert_list_data_to_lightweight_charts_format(res.data.data)
    })
  }

  const renderChart = () => {

    chartRef.current = createChart("chart", {
      width: 390,
      height: 280,
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

    const promiseArray = intervals.map((interval) => fetchData(symbol_type, symbol, interval, 1, 1000))

    Promise.all(promiseArray).then((dataArray) => {
      dataArray.forEach((data, index) => {
        seriesesData.set(intervals[index], data)
      })
      renderChart()
      syncToInterval(intervals[0])
    })
  }, []); // 注意这里的空依赖数组

  const handleChangeSwitcher = (e) => {
    const interval = e.target.value
    syncToInterval(interval)
  }


  return (
        <>
          <div
            style={{
              padding: '12px',
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
              <Title level={4}>【{symbol}】价格图表</Title>
              <div id="chart"></div>
              <Radio.Group defaultValue={intervals[0]} buttonStyle="solid" onChange={handleChangeSwitcher}>
                {
                  intervals.map((interval, index) => {
                    return <Radio.Button key={index} value={interval}>{interval}</Radio.Button>
                  })
                }
              </Radio.Group>
            </Space>
          </div>
        </>
  );
};


export default Container;



