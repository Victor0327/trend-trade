import React, { useState } from 'react';
import { Input, Modal, Form, DatePicker } from 'antd';
const App = (props) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [form] = Form.useForm()

  const handleOk = () => {
    setConfirmLoading(true);
    form.validateFields().then((values) => {
      values.close_date = values.close_date.format('YYYY-MM-DD HH:mm:ss');
      values.id = props.closePositionData.id
      values.risk_amount_currency = props.closePositionData.risk_amount_currency
      values.risk_amount = props.closePositionData.risk_amount
      props.onOk(values)
      setConfirmLoading(false);
    }).catch(() => {
      setConfirmLoading(false);
    })
  };

  return (
    <>
      <Modal
        title="平仓"
        open={props.open}
        onOk={handleOk}
        confirmLoading={confirmLoading}
        onCancel={props.onCancel}
      >
        <Form
          labelCol={{ xs: { span: 8 }, sm: { span: 4 } }}
          wrapperCol={{ xs: { span: 16 }, sm: { span: 12 } }}
          layout="horizontal"
          form={form}
          initialValues={{
            layout: "horizontal",
          }}
          // onValuesChange={onValuesChange}
          style={{
            width: '100%',
            borderRadius: 6,
            paddingTop: 24,
          }}
        >
          <Form.Item label="平仓时间" name="close_date" rules={[{required: true}]}
          >
            <DatePicker showTime/>
          </Form.Item>
          <Form.Item label="收益(R)" name="result" rules={[{required: true}]}
          >
            <Input
              placeholder="输入收益(R)"
              type="number"
            />
          </Form.Item>
          <Form.Item label="备注" name="memo"
          >
            <Input
              placeholder="输入备注"
              type="text"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
export default App;