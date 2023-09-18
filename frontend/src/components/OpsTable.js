import React from 'react';
import { Space, Table, Tag, Button } from 'antd';


// const data = [
//   {
//     key: '1',
//     version: 'John Brown',
//     canary_percentage: 32,
//     memo: 'New York No. 1 Lake Park',
//     created_at: 'New York No. 1 Lake Park',
//     tags: ['active'],
//   },
// ];

const App = (props) => {
  const columns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Interval',
      dataIndex: 'interval',
      key: 'interval',
    },
    {
      title: 'Period',
      dataIndex: 'period',
      key: 'period',
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button onClick={() => props.onClick(record)}>Edit</Button>
        </Space>
      ),
    },
  ];

  return <Table columns={columns} dataSource={props.data} />
};
export default App;