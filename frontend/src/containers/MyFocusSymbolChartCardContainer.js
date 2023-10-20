import React, { useState, useEffect } from 'react';
import { Col, Row, theme, Pagination, Spin } from 'antd';
import { useParams } from 'react-router-dom';

import { commonService } from '../services/CommonService'
import SymbolChartCard from '../components/SymbolChartCard'



const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const { type } = useParams();

  const [listData, setListData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [count, setCount] = useState(100);
  const [currentPagination, setCurrentPagination] = useState(1);

  const handleChangePagination = (currentPagination) => {
    setCurrentPagination(currentPagination)
    renderPage(currentPagination)
  }

  const renderPage = (currentPagination) => {
    setListData(
      []
    )
    setIsLoading(true)

    commonService.get(`/my_focus/list?type=${type}&page=${currentPagination}&limit=10`).then((result) => {

      setListData(result.data.data.list)

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
            <Spin tip="Loading" size="large" spinning={isLoading}>
              <Row gutter={16}>
                {listData.map((item, index) =>
                  <Col key={index} span={24}>
                    <SymbolChartCard
                      symbol={item.symbol}
                      type={item.type}
                      symbolTitle={item.symbol_title}
                    ></SymbolChartCard>
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



