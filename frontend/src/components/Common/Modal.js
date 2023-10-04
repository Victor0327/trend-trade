import React, { useState } from 'react';
import { Button, Modal } from 'antd';
const App = (props) => {
  const [confirmLoading, setConfirmLoading] = useState(false);

  const handleOk = () => {
    setConfirmLoading(true);
    props.handleOk().then(() => {
      props.handleCloseModal();
      setConfirmLoading(false);
    },() => {
      props.handleCloseModal();
      setConfirmLoading(false);
    })

  };
  const handleCancel = () => {
    console.log('Clicked cancel button');
    props.handleCloseModal();
  };
  return (
    <>
      <Modal
        title={props.title}
        open={props.open}
        onOk={handleOk}
        confirmLoading={confirmLoading}
        onCancel={handleCancel}
      >
        {props.children}
      </Modal>
    </>
  );
};
export default App;