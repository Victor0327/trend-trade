import React, { useState, useEffect } from 'react';
import { Card, Col, Row, theme, Pagination, Spin } from 'antd';
import { useParams } from 'react-router-dom';

import { createChart } from 'lightweight-charts';
import { transferOpsList } from '../utils/transferModel'

import { commonService } from '../services/CommonService'
import OpsTable from '../components/OpsTable'
import BarCard from '../components/BarCard'



const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const { date } = useParams();

  const [listData, setListData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [count, setCount] = useState(100);
  const [currentPagination, setCurrentPagination] = useState(1);

  const handleTableEdit = (res) => {}

  const handleChangePagination = (currentPagination) => {
    setCurrentPagination(currentPagination)
    renderPage(currentPagination)
  }

  const renderPage = (currentPagination) => {
    setListData(
      []
    )
    setIsLoading(true)

    commonService.get(`/ops/${date}/list?page=${currentPagination}&limit=10`).then((result) => {

      setListData(
        transferOpsList(result.data.data.list)
      )

      setCount(result.data.data.count)
      setIsLoading(false)
    }, err => {
      setListData([])
      setCount(200)
      setIsLoading(false)
    })


  }


  useEffect(() => {

    renderPage(currentPagination)
  }, []); // 注意这里的空依赖数组


  return (
        <>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            {/* <OpsTable data={listData} onClick={handleTableEdit}></OpsTable> */}
            <Spin tip="Loading" size="large" spinning={isLoading}>
              <Row gutter={16}>
                {listData.map((item, index) =>
                  <Col key={index} span={12}>
                    <BarCard
                      symbol={item.symbol}
                      interval={item.interval}
                      period={item.period}
                    ></BarCard>
                  </Col>
                )}
              </Row>
              <Pagination defaultCurrent={1}
                current={currentPagination} onChange={handleChangePagination} total={count}
                showSizeChanger={false}
              />
            </Spin>

          </div>
        </>
  );
};


export default Container;



