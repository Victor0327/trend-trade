import React, { useState, useEffect } from 'react';
import { Breadcrumb, Layout, Menu, theme } from 'antd';
import { createChart } from 'lightweight-charts';

import { commonService } from '../services/CommonService'


const renderChart = () => {
  const chartOptions = { layout: { textColor: 'black', background: { type: 'solid', color: 'white' } }, width: 800, height: 300 };
    const chart = createChart("chart", chartOptions);
    const candlestickSeries = chart.addCandlestickSeries(
      { upColor: '#26a69a', downColor: '#ef5350', borderVisible: false, wickUpColor: '#26a69a', wickDownColor: '#ef5350' }
      );

    commonService.get('/trade/alert').then((res) => {

      // const data = [
      //   { open: 10, high: 10.63, low: 9.49, close: 9.55, time: 1642427876 },
      //   { open: 9.55, high: 10.30, low: 9.42, close: 9.94, time: 1642514276 }, { open: 9.94, high: 10.17, low: 9.92, close: 9.78, time: 1642600676 }, { open: 9.78, high: 10.59, low: 9.18, close: 9.51, time: 1642687076 }, { open: 9.51, high: 10.46, low: 9.10, close: 10.17, time: 1642773476 }, { open: 10.17, high: 10.96, low: 10.16, close: 10.47, time: 1642859876 }, { open: 10.47, high: 11.39, low: 10.40, close: 10.81, time: 1642946276 }, { open: 10.81, high: 11.60, low: 10.30, close: 10.75, time: 1643032676 }, { open: 10.75, high: 11.60, low: 10.49, close: 10.93, time: 1643119076 }, { open: 10.93, high: 11.53, low: 10.76, close: 10.96, time: 1643205476 }];
      // console.log(res.data)

      candlestickSeries.setData(res.data.data);

    })

    chart.timeScale().fitContent();

}


const BarDetailContainer = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  useEffect(() => {

    renderChart()
  }, []); // 注意这里的空依赖数组


  return (
        <>
          <Breadcrumb
            style={{
              margin: '16px 0',
            }}
          >
            <Breadcrumb.Item>User</Breadcrumb.Item>
            <Breadcrumb.Item>Bill</Breadcrumb.Item>
          </Breadcrumb>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            <div id="chart"></div>
          </div>
        </>
  );
};


export default BarDetailContainer;



