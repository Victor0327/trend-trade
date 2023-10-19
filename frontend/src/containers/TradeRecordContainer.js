import { Helmet } from 'react-helmet';
import React, { useState, useEffect, useRef } from 'react';
import { theme, Space, Table, Typography, Button, Flex, Popconfirm, message } from 'antd';
import Message from '../components/Common/Message'
import { getColumnSearchProps } from '../components/Common/ColumnSearch'
import { renderChart, setSeriesData, addSeries } from './helper/tradeRecordChart'
import TradeRecordClosePositionModal from './helper/tradeRecordClosePositionModal'
import TradeRecordOpenPositionModal from './helper/tradeRecordOpenPositionModal'

import { commonService } from '../services/CommonService'

const { Title } = Typography;
const ref = React.createRef();


const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const [searchText, setSearchText] = useState('');
  const [searchedColumn, setSearchedColumn] = useState('');
  const searchInput = useRef(null);

  const cnyChartRef = useRef(null);
  const usdChartRef = useRef(null);

  const cnySeriesRef = useRef(null);
  const usdSeriesRef = useRef(null);



  const handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = (clearFilters) => {
    clearFilters();
    setSearchText('');
  };

  const [cnyAccountTableData, setCnyAccountTableData] = useState([]);
  const [usdAccountTableData, setUsdAccountTableData] = useState([]);

  const [closePositionModalOpen, setClosePositionModalOpen] = useState(false);
  const [closePositionData, setClosePositionData] = useState({});

  const [openPositionModalOpen, setOpenPositionModalOpen] = useState(false);
  const [openPositionData, setOpenPositionData] = useState({});




  const fetchTableData = (risk_amount_currency, risk_amount) => {
    return commonService.get(`/trade_record/list?risk_amount_currency=${risk_amount_currency}&risk_amount=${risk_amount}`).then(res => res.data.data)
  }

  const get_cumulative_sum_data = (risk_amount_currency, risk_amount) => {
    return commonService.get(`/trade_record/cumulative_sum?risk_amount_currency=${risk_amount_currency}&risk_amount=${risk_amount}`).then(res => res.data.data)
  }


  useEffect(() => {
    renderChart(cnyChartRef, 'cny_chart')
    addSeries(cnyChartRef, cnySeriesRef)

    renderChart(usdChartRef, 'usd_chart')
    addSeries(usdChartRef, usdSeriesRef)

    refreshCNYData()
    refreshUSDData()

    return () => {

    }
  }, [])

  const columns = [
    {
      title: '开仓时间',
      key: 'open_date',
      dataIndex: 'open_date',
      render: (text) => {
        return text ? text.split('T')[0] : null;
      }
    },
    {
      title: '标的',
      key: 'symbol',
      dataIndex: 'symbol',
    },
    {
      title: '风险(R)',
      key: 'risk',
      dataIndex: 'risk',
    },
    {
      title: '收益(R)',
      key: 'result',
      dataIndex: 'result',
    },
    {
      title: '策略',
      key: 'strategy_name',
      dataIndex: 'strategy_name',
      ...getColumnSearchProps('strategy_name', searchText, searchedColumn, searchInput, handleSearch, handleReset, setSearchText, setSearchedColumn),
    },
    {
      title: '表现',
      key: 'strategy_requirement_performance_array',
      dataIndex: 'strategy_requirement_performance_array',
      render: (array) => {
        return array.map(item => item[1]).join(',')
      }
    }
  ]
  const cnyColumns = [
    ...columns,
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Flex
          gap="small"
          vertical
        >
            {
              record['result'] === ''
              &&
              <Button default size="small"
                onClick={() => {
                  setClosePositionModalOpen(true)
                  setClosePositionData({
                    ...record,
                    risk_amount_currency: 'CNY',
                    risk_amount: 2000
                  })
                }}
              >平仓</Button>
            }
            <Popconfirm
              title="删除记录"
              description="确定删除记录吗?"
              onConfirm={() => deleteConfirm(record, 'CNY', 2000)}
              okText="Yes"
              cancelText="No"
            >
              <Button type="text" size="small">删除</Button>
            </Popconfirm>
        </Flex>
      ),
    }
  ]

  const usdColumns = [
    ...columns,
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Flex
          gap="small"
          vertical
        >
            {
              record['result'] === ''
              &&
              <Button default size="small"
                onClick={() => {
                  setClosePositionModalOpen(true)
                  setClosePositionData({
                    ...record,
                    risk_amount_currency: 'USD',
                    risk_amount: 100
                  })
                }}
              >平仓</Button>
            }
            <Popconfirm
              title="删除记录"
              description="确定删除记录吗?"
              onConfirm={() => deleteConfirm(record, 'USD', 100)}
              okText="Yes"
              cancelText="No"
            >
              <Button type="text" size="small" >删除</Button>
            </Popconfirm>
        </Flex>
      ),
    }
  ]


  // delete 区域

  const deleteConfirm = (data, risk_amount_currency, risk_amount) => {
    commonService.post('/trade_record/delete_data',
      {
        id: data.id,
        risk_amount,
        risk_amount_currency
      }
    ).then(() => {
      message.success('删除成功！');

      if (risk_amount_currency === 'CNY') {
        refreshCNYData()
      } else {
        refreshUSDData()
      }
    })
  };

  const openPosition = (values) => {
    commonService.post('/trade_record/open_position', values).then(() => {
      message.success('开仓成功！');
      if (values.risk_amount_currency === 'CNY') {
        refreshCNYData()
      } else {
        refreshUSDData()
      }
    })
  }

  const closePosition = (values) => {
    commonService.post('/trade_record/close_position', values).then(() => {
      message.success('平仓成功！');
      if (values.risk_amount_currency === 'CNY') {
        refreshCNYData()
      } else {
        refreshUSDData()
      }
    })
  }

  const refreshCNYData = () => {
    fetchTableData('CNY', 2000).then((data) => {
      setCnyAccountTableData(data)
    })
    get_cumulative_sum_data('CNY', 2000).then((data) => {
      const seriesData = data.map(item => ({ time: item['open_date'].split('T')[0], value: item['cumulative_result']}))
      setSeriesData(cnySeriesRef, seriesData)
    })
  }

  const refreshUSDData = () => {
    fetchTableData('USD', 100).then((data) => {
      setUsdAccountTableData(data)
    })

    get_cumulative_sum_data('USD', 100).then((data) => {
      const seriesData = data.map(item => ({ time: item['open_date'].split('T')[0], value: item['cumulative_result']}))
      setSeriesData(usdSeriesRef, seriesData)
    })
  }


  return (
        <>
          <Helmet>
            <title>交易记录</title>
            <meta name="description" content="记录你的交易 - victor trade" />
          </Helmet>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            <div>
              <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                <Title level={4}>交易记录</Title>
                <Flex
                  style={{
                    marginBottom: -10
                  }}
                  justify="space-between"
                  align="center"
                  horizontal
                >
                  <h3>人民币账户-风险资金2000CNY</h3>
                  <Button type="primary" size="small"
                    onClick={() => {
                      setOpenPositionModalOpen(true)
                      setOpenPositionData({
                        risk_amount_currency: 'CNY',
                        risk_amount: 2000
                      })
                    }}
                  >开仓</Button>
                </Flex>
                <div id="cny_chart"></div>
                <Table columns={cnyColumns} dataSource={cnyAccountTableData} size="small" />

                <Flex
                  style={{
                    marginBottom: -10
                  }}
                  justify="space-between"
                  align="center"
                  horizontal
                >
                  <h3>美元账户-风险资金100USD</h3>
                  <Button type="primary" size="small"
                    onClick={() => {
                      setOpenPositionModalOpen(true)
                      setOpenPositionData({
                        risk_amount_currency: 'USD',
                        risk_amount: 100
                      })
                    }}
                  >开仓</Button>
                </Flex>

                <div id="usd_chart"></div>
                <Table columns={usdColumns} dataSource={usdAccountTableData} size="small" />
              </Space>
            </div>
          </div>

          <Message ref={ref}></Message>
          <TradeRecordClosePositionModal
            closePositionData={closePositionData}
            open={closePositionModalOpen}
            onCancel={() => { setClosePositionModalOpen(false) }}
            onOk={(values) => {
              closePosition(values)
              setClosePositionModalOpen(false)
            }}
          ></TradeRecordClosePositionModal>

          <TradeRecordOpenPositionModal
            openPositionData={openPositionData}
            open={openPositionModalOpen}
            onCancel={() => { setOpenPositionModalOpen(false) }}
            onOk={(values) => {
              openPosition(values)
              setOpenPositionModalOpen(false)
            }}
          ></TradeRecordOpenPositionModal>
        </>
  );
};


export default Container;



