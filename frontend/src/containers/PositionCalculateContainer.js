import { Helmet } from 'react-helmet';
import snakeCase from 'lodash.snakecase'
import mapKeys from 'lodash.mapkeys'
import { useState, useEffect } from 'react';

import { theme, Form, Input, Button, Descriptions, Space } from 'antd';

import Select from '../components/Common/Select'
import { commonService } from '../services/CommonService'
import { calculate_descriptions_map } from '../utils/transferModel'

var symbol_list = []

const App = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const [form] = Form.useForm()
  const [optionsSelect, setOptionsSelect] = useState([])
  const [descriptionsItems, setDescriptionsItems] = useState([])
  const [loading, setLoading] = useState(false)

  const [profitCurrency, setProfitCurrency] = useState('CNY')
  const [accountCurrency, setAccountCurrency] = useState('CNY')

  const onChangeSelect = (value) => {
    const selected_symbol = symbol_list.find(obj => obj.symbol === value);
    if (selected_symbol.type === 'cn_goods' ) {
      setProfitCurrency('CNY')
      setAccountCurrency('CNY')
    } else if (selected_symbol.type === 'currency' ) {
      setProfitCurrency(selected_symbol.symbol.slice(-3))
      setAccountCurrency('USD')
    } else if (selected_symbol.type === 'us_goods' ) {
      setProfitCurrency('USD')
      setAccountCurrency('USD')
    } else if (selected_symbol.type === 'crypto' ) {
      setProfitCurrency('USD')
      setAccountCurrency('USD')
    }

  };

  const onSearchSelect = (value) => {
    console.log('search:', value);
  };

  const onValuesChange = (data) => {
  };

  const onClickReset = () => {
    form.resetFields()
  }

  const onFinish = (data) => {
    setLoading(true)
    const selected_symbol = symbol_list.find(obj => obj.symbol === data.symbol);
    let payload = {
      ...data,
      marginLevel: data.marginLevel * 0.01,
      entryPrice: +data.entryPrice,
      slPrice: +data.slPrice,
      tpPrice: +data.tpPrice,
      riskAmount: +data.riskAmount,
      symbolType: selected_symbol.type,
    }

    payload = mapKeys(payload, (value, key) => snakeCase(key));

    commonService.post('/position_calculate', payload).then(res => {
      setLoading(false)

      const items = Object.entries(res.data.data).map((item, index) => ({
        label: calculate_descriptions_map[item[0]],
        children: item[1]
      }))

      setDescriptionsItems(items)
    })
  };


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

  useEffect(() => {

    fetchSymbolData()
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    }
  }, [])


  return (
    <>
      <Helmet>
        <title>仓位计算器</title>
        <meta name="description" content="欢迎使用仓位计算器 - victor trade" />
        <link rel="icon" href="/calculator_icon.ico" />
      </Helmet>
      <div
        style={{
          paddingTop: 30,
          paddingLeft: 24,
          paddingRight: 24,
          height: 840,
          background: colorBgContainer,
        }}
      >

        <Form
          labelCol={{ xs: { span: 8 }, sm: { span: 4 } }}
          wrapperCol={{ xs: { span: 16 }, sm: { span: 12 } }}
          layout="horizontal"
          form={form}
          initialValues={{
            layout: "horizontal",
          }}
          onValuesChange={onValuesChange}
          onFinish={onFinish}
          style={{
            maxWidth: 600,
            width: '100%',
            // height: 470,
            borderRadius: 6,
            paddingTop: 24,
          }}
        >
          <Form.Item label="品种"
            name="symbol"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Select
              // style={{
              //   width: 200,
              // }}
              placeholder="选择品种"
              onChange={onChangeSelect}
              onSearch={onSearchSelect}
              options={optionsSelect}
            ></Select>
          </Form.Item>
          <Form.Item label="开仓价"
            name="entryPrice"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Input
              placeholder="输入开仓价"
              type="number"
              suffix={profitCurrency}
            />
          </Form.Item>
          <Form.Item label="止损价"
            name="slPrice"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Input
              placeholder="输入止损价"
              type="number"
              suffix={profitCurrency}
            />
          </Form.Item>
          <Form.Item label="止盈价"
            name="tpPrice"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Input
              placeholder="输入止盈价"
              type="number"
              suffix={profitCurrency}
            />
          </Form.Item>
          <Form.Item label="风险资金"
            name="riskAmount"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Input
              placeholder="输入风险资金"
              type="number"
              suffix={accountCurrency}
            />
          </Form.Item>
          <Form.Item label="保证金比例"
            name="marginLevel"
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Input
              placeholder="输入保证金比例"
              type="number"
              suffix="%"
            />
          </Form.Item>
          <Form.Item
            wrapperCol={{ xs: { span: 4 }, sm: { span: 4, offset: 4 } }}
          >
            <Space size={30}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
              >计算</Button>

              <Button
                  type="default"
                  onClick={onClickReset}
              >重置</Button>
            </Space>

          </Form.Item>

        </Form>

        {
          descriptionsItems.length > 0 &&
          <Descriptions
            title="计算结果"
            bordered
            column={{
              xs: 1,
              sm: 2,
              md: 3,
              lg: 3,
              xl: 4,
              xxl: 4,
            }}
            items={descriptionsItems}
          />
        }


        {/* <Flex
          style={{
            width: '100%',
            height: 300,
            borderRadius: 6,
            paddingTop: 24,
          }}
          justify="center"
          align="flex-start">

        </Flex> */}
      </div>
    </>
  )
}

export default App