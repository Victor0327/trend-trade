import React from 'react';
import { Space, Table, Tag, Button } from 'antd';

import CanaryProgress from './CanaryProgress'

import toLocalDateTime from '../../utils/date'

const App = (props) => {
  const columns = [
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'Canary Percentage',
      dataIndex: 'canary_percentage',
      key: 'canary_percentage',
      render: (text) => (<CanaryProgress value={text}></CanaryProgress>)
    },
    {
      title: 'Memo',
      dataIndex: 'memo',
      key: 'memo',
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => toLocalDateTime(text),
    },
    {
      title: 'Tags',
      key: 'tags',
      dataIndex: 'tags',
      render: (_, { tags }) => (
        <>
          {tags.map((tag) => {
            let color = tag.length > 5 ? 'geekblue' : 'green';
            if (tag === 'loser') {
              color = 'volcano';
            }
            return (
              <Tag color={color} key={tag}>
                {tag.toUpperCase()}
              </Tag>
            );
          })}
        </>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          {
            record.tags.includes('active')?
              <Button onClick={() => props.onClick(record.version, record.canary_percentage, record.memo)}>Edit</Button>
            :
            <div>
            </div>
          }
        </Space>
      ),
    },
  ];

  return <Table columns={columns} dataSource={props.data} />
};
export default App;