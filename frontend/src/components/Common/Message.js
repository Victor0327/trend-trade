import React, { useImperativeHandle, forwardRef } from 'react';

import { message } from 'antd';
const App = forwardRef((props, ref) => {
  const [messageApi, contextHolder] = message.useMessage();

  useImperativeHandle(ref, () => ({
    success(content) {
      messageApi.open({
        type: 'success',
        content: content,
      });
    },
    error(content) {
      messageApi.open({
        type: 'error',
        content: content,
      });
    },
    warning(content) {
      messageApi.open({
        type: 'warning',
        content: content,
      });
    }
  }));


  return (
    <>
      {contextHolder}
    </>
  );
});
export default App;