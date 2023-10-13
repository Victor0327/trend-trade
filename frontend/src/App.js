/* eslint-disable jsx-a11y/anchor-has-content */
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import {
  DesktopOutlined,
  FileOutlined,
  PieChartOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { ConfigProvider, Layout, Menu, theme, Space } from 'antd';
// import AipContainer from './containers/AipContainer'
import BarDetailContainer from './containers/BarDetailContainer'
import DateOpsContainer from './containers/DateOpsContainer'
import SymbolChartContainer from './containers/SymbolChartContainer'
import SymbolsContainer from './containers/SymbolsContainer'
import PositionCalculateContainer from './containers/PositionCalculateContainer'

const { Header, Content, Footer, Sider } = Layout;
var itemKey = 0
function getItem(label, icon, children) {
  itemKey ++
  return {
    key: itemKey,
    icon,
    children,
    label,
  };
}
const items = [
  getItem('定期投资',
  <Space size={1}>
    <FileOutlined />
    <a href="/aip/list"/>
  </Space>),
  getItem('行情数据',
  <Space size={1}>
    <FileOutlined />
    <a href="/symbols"/>
  </Space>),
  getItem('仓位计算器',
  <Space size={1}>
    <FileOutlined />
    <a href="/position_calculate"/>
  </Space>),
];
const App = () => {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  return (
    <ConfigProvider
        theme={{
          components: {
            Layout: {
              headerHeight: 20
            }
          },
        }}
      >
      <Layout
        style={{
          minHeight: '100vh',
        }}
      >
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          zeroWidthTriggerStyle={{
            top: 10,
          }}
          collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}
        >
          <div className="demo-logo-vertical" />
          <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" items={items} />
        </Sider>
        <Layout>
          {/* <Header
            style={{
              padding: 0,
              background: colorBgContainer,
            }}
          /> */}
          <Content
            style={{
              // margin: '0 16px',
            }}
          >
            <Router>
                <Routes>
                  <Route path="/" element={ <Navigate to="/symbols" /> } />
                  {/* <Route path="/aip/list" element={<AipListContainer />}></Route> */}
                  <Route path="/symbols" element={<SymbolsContainer />}></Route>
                  <Route path="/bar/detail" element={<BarDetailContainer />}></Route>
                  <Route path="/symbol/:symbol_type/:symbol" element={<SymbolChartContainer />}></Route>
                  <Route path="/ops/:date" element={<DateOpsContainer />}></Route>
                  <Route path="/position_calculate" element={<PositionCalculateContainer />}></Route>
                </Routes>
            </Router>
          </Content>
          <Footer
            style={{
              textAlign: 'center',
            }}
          >
            Victor Trade ©2023 Created by victor
          </Footer>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
};
export default App;
