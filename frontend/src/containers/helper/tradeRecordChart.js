import { createChart } from 'lightweight-charts';

const addSeries = (chartRef, seriesRef) => {
  seriesRef.current = chartRef.current.addBaselineSeries({ baseValue: { type: 'price', price: 0 }, topLineColor: 'rgba( 38, 166, 154, 1)', topFillColor1: 'rgba( 38, 166, 154, 0.28)', topFillColor2: 'rgba( 38, 166, 154, 0.05)', bottomLineColor: 'rgba( 239, 83, 80, 1)', bottomFillColor1: 'rgba( 239, 83, 80, 0.05)', bottomFillColor2: 'rgba( 239, 83, 80, 0.28)' });
}

const setSeriesData = (seriesRef, seriesData) => {
  seriesRef.current.setData(seriesData)
}

const renderChart = (chartRef, chartId) => {
  chartRef.current = createChart(chartId, {
    width: 370,
    height: 200,
    layout: {
      textColor: 'black',
      background: { type: 'solid', color: 'white' }
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

export {
  renderChart,
  addSeries,
  setSeriesData
}