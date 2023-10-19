import React, { useState, useEffect } from 'react';
import { Input, Modal, Form, DatePicker, Select } from 'antd';

import { commonService } from '../../services/CommonService'

var symbol_list = []

const App = (props) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [optionsSelect, setOptionsSelect] = useState([])
  const [strategySelect, setStrategySelect] = useState([])
  const [strategyRequirement, setStrategyRequirement] = useState([])

  const [form] = Form.useForm()

  const handleOk = () => {
    setConfirmLoading(true);
    form.validateFields().then((values) => {
      values.open_date = values.open_date.format('YYYY-MM-DD HH:mm:ss');
      values.risk_amount_currency = props.openPositionData.risk_amount_currency
      values.risk_amount = props.openPositionData.risk_amount
      const selected_symbol = symbol_list.find(obj => obj.symbol === values.symbol);
      values.symbol_type = selected_symbol.type
      values.strategy_requirement_performance_array = Object.entries(values)
      .filter(([key]) => key.includes('strategy_requirement_performance_')).map(item => {
        return [
          item[0].split('strategy_requirement_performance_')[1],
          item[1]
        ]
      })
      console.log(values)
      props.onOk(values)
      setConfirmLoading(false);
    }).catch((e) => {
      console.log(e)
      setConfirmLoading(false);
    })
  };

  const fetchStrategy = () => {
    return commonService.get('/trade_record/strategy').then(res => res.data.data)
  }

  const fetchStrategyRequirement = (strategy_id) => {
    return commonService.get(`/trade_record/strategy_requirement?strategy_id=${strategy_id}`).then(res => res.data.data)
  }

  const fetchSymbolData = () => {
    const cn_goods_promise = commonService.get('/symbols?type=cn_goods')
    const currency_promise = commonService.get('/symbols?type=currency')
    const us_goods_promise = commonService.get('/symbols?type=us_goods')
    const crypto_promise = commonService.get('/symbols?type=crypto')



    Promise.all(
      [
        cn_goods_promise,
        currency_promise,
        us_goods_promise,
        crypto_promise,
      ]
    ).then(([cn_goods_data, currency_data, us_goods_data, crypto_promise_data]) => {
      const data = [
        ...cn_goods_data.data.data,
        ...currency_data.data.data,
        ...us_goods_data.data.data,
        ...crypto_promise_data.data.data,
      ]
      symbol_list = data
      setOptionsSelect(data.map((item, index) => {
        return {
          label: item.symbol_title,
          value: item.symbol
        }
      }))
    })
  }

  const onChangeStrategy = (strategy_id) => {
    console.log(strategy_id)
    fetchStrategyRequirement(strategy_id).then(requirements => {
      setStrategyRequirement(requirements.map(item => ({
        label: item.title,
        value: item.id
      })))
    })
  }

  useEffect(() => {

    fetchSymbolData()
    fetchStrategy().then(strategies => {
      setStrategySelect(strategies.map(item => ({
        label: item.name,
        value: item.id
      })))
      fetchStrategyRequirement(strategies[0].id).then(requirements => {
        setStrategyRequirement(requirements.map(requirement => ({
          label: requirement.title,
          value: requirement.id
        })))
      })
    })
    // document.body.style.overflow = 'hidden';
    return () => {
      // document.body.style.overflow = '';
    }
  }, [])

  return (
    <>
      <Modal
        title="开仓"
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
          <Form.Item label="开仓时间" name="open_date" rules={[{required: true}]}
          >
            <DatePicker showTime/>
          </Form.Item>
          <Form.Item label="品种"
            name="symbol"
            rules={[{required: true}]}
          >
            <Select
              placeholder="选择品种"
              showSearch={true}
              options={optionsSelect}
            ></Select>
          </Form.Item>

          <Form.Item label="策略"
            name="strategy_id"
            rules={[{required: true}]}
          >
            <Select
              placeholder="选择策略"
              showSearch={true}
              onChange={onChangeStrategy}
              options={strategySelect}
            ></Select>
          </Form.Item>

          {
            strategyRequirement.map(requirement => (
              <Form.Item label={requirement.label}
                name={`strategy_requirement_performance_${requirement.value}`}
                rules={[{required: true}]}
              >
                <Select
                  placeholder="策略表现"
                  showSearch={true}
                  options={[
                    { value: 'S', label: 'S' },
                    { value: 'A', label: 'A' },
                    { value: 'B', label: 'B' },
                    { value: 'C', label: 'C' },
                  ]}
                >
                </Select>
              </Form.Item>
            ))
          }

          <Form.Item label="风险(R)" name="risk" rules={[{required: true}]}
          >
            <Input
              placeholder="输入风险(R)"
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