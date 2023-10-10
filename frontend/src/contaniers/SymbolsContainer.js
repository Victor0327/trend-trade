import React, { useState, useEffect, useRef } from 'react';
import { Breadcrumb, theme, Button, Space, Input, Table } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import Modal from '../components/Common/Modal'
import Message from '../components/Common/Message'
import { getColumnSearchProps } from '../components/Common/ColumnSearch'

import { commonService } from '../services/CommonService'

const ref = React.createRef();


const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const [searchText, setSearchText] = useState('');
  const [searchedColumn, setSearchedColumn] = useState('');
  const searchInput = useRef(null);

  const handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = (clearFilters) => {
    clearFilters();
    setSearchText('');
  };

  const [cryptoTableData, setCryptoTableData] = useState([]);
  const [USGoodsTableData, setUSGoodsTableData] = useState([]);
  const [CNGoodsTableData, setCNGoodsTableData] = useState([]);
  const [currencyTableData, setCurrencyTableData] = useState([]);



  const fetchTableData = (type) => {
    return commonService.get(`/symbols?type=${type}`).then(res => res.data.data)
  }


  useEffect(() => {
    fetchTableData('crypto').then((data) => {
      setCryptoTableData(data)
    })
    fetchTableData('cn_goods').then((data) => {
      setCNGoodsTableData(data)
    })
    fetchTableData('us_goods').then((data) => {
      setUSGoodsTableData(data)
    })
    fetchTableData('currency').then((data) => {
      setCurrencyTableData(data)
    })

    return () => {

    }
  }, [])

  const symbolsColumns = [
    {
      title: '标的缩写',
      key: 'symbol',
      dataIndex: 'symbol',
      ...getColumnSearchProps('symbol', searchText, searchedColumn, searchInput, handleSearch, handleReset, setSearchText, setSearchedColumn),
    },
    {
      title: '标的名称',
      key: 'symbol_title',
      dataIndex: 'symbol_title',
      ...getColumnSearchProps('symbol_title', searchText, searchedColumn, searchInput, handleSearch, handleReset, setSearchText, setSearchedColumn),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <a href={`/symbol/${record.type}/${record.symbol}`}
          // target="_blank"
          rel="noopener noreferrer">查看行情</a>
        </Space>
      ),
    },
  ]



  return (
        <>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            <div>
              <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                <Breadcrumb
                  style={{
                    margin: '60px 0 0 0',
                  }}
                >
                  <Breadcrumb.Item>标的列表</Breadcrumb.Item>
                </Breadcrumb>
                <Table columns={symbolsColumns} dataSource={cryptoTableData} size="small" />
                <Table columns={symbolsColumns} dataSource={USGoodsTableData} size="small" />
                <Table columns={symbolsColumns} dataSource={CNGoodsTableData} size="small" />
                <Table columns={symbolsColumns} dataSource={currencyTableData} size="small" />
              </Space>
            </div>
          </div>

          <Message ref={ref}></Message>
        </>
  );
};


export default Container;



