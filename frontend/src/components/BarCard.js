import React, { useState, useEffect } from 'react';
import { Card } from 'antd';
import { createChart } from 'lightweight-charts';

import { commonService } from '../services/CommonService'

const App = (props) => {

  const renderChart = () => {
      const chartContainer = document.getElementById(props.symbol);
      const chartOptions = { layout: { textColor: 'black', background: { type: 'solid', color: 'white' } }
        , width: chartContainer.clientWidth, height: chartContainer.clientHeight
      };
      const chart = createChart(chartContainer, chartOptions);
      const candlestickSeries = chart.addCandlestickSeries({ upColor: '#26a69a', downColor: '#ef5350', borderVisible: false, wickUpColor: '#26a69a', wickDownColor: '#ef5350' });

      commonService.get(`/symbol_candle_data/${props.symbol}?interval=${props.interval}&period=${props.period}`).then((res) => {

        candlestickSeries.setData(res.data.data);

      })

      chart.timeScale().fitContent();
      window.addEventListener('resize', () => {
        chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
      });

  }

  useEffect(() => {

    renderChart()
  }, []); // 注意这里的空依赖数组

  return (
    <Card title={props.symbol} >
      <div id={props.symbol} style={{ width: '100%', height: '400px' }}></div>
    </Card>
  )
};
export default App;