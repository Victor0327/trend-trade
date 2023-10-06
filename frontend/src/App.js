/* eslint-disable jsx-a11y/anchor-has-content */
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import {
  DesktopOutlined,
  FileOutlined,
  PieChartOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Layout, Menu, theme, Space } from 'antd';
import BarDetailContainer from './contaniers/BarDetailContainer'
import DateOpsContainer from './contaniers/DateOpsContainer'
import SymbolChartContainer from './contaniers/SymbolChartContainer'
// import AipContainer from './contaniers/AipContainer'

const { Header, Content, Footer, Sider } = Layout;
function getItem(label, key, icon, children) {
  return {
    key,
    icon,
    children,
    label,
  };
}
const items = [
  getItem('定期投资', '1',
  <Space size={1}>
    <FileOutlined />
    <a href="/aip/list"/>
  </Space>),
  getItem('Option', '2', <><PieChartOutlined href="/bar/detail"/></>),
  getItem('Option', '3', <DesktopOutlined />),
  getItem('User', 'sub1', <UserOutlined />, [
    getItem('Tom', '4', <><PieChartOutlined /><a href="/bar/detail"/></>),
    getItem('Bill', '5'),
    getItem('Alex', '6'),
  ]),
  getItem('Files', '7', <FileOutlined />),
];
const App = () => {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  return (
    <Layout
      style={{
        minHeight: '100vh',
      }}
    >
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div className="demo-logo-vertical" />
        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: 0,
            background: colorBgContainer,
          }}
        />
        <Content
          style={{
            margin: '0 16px',
          }}
        >
          <Router>
              <Routes>
                {/* <Route path="/aip/list" element={<AipListContainer />}></Route> */}
                <Route path="/bar/detail" element={<BarDetailContainer />}></Route>
                <Route path="/symbol/:symbol_type/:symbol" element={<SymbolChartContainer />}></Route>
                <Route path="/ops/:date" element={<DateOpsContainer />}></Route>
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
  );
};
export default App;
