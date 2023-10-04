import React, { useState, useEffect } from 'react';
import { Breadcrumb, theme, Button, Space, Input, Switch, Row, Col, Radio } from 'antd';
import Modal from '../components/Common/Modal'
import Message from '../components/Common/Message'

import AipDetailListTable from '../components/Aip/AipDetailListTable'

import { commonService } from '../services/CommonService'

const ref = React.createRef();

const CONFIG_VALUE_PRICE_AREA_PANIC = 'panic'
const CONFIG_VALUE_PRICE_AREA_UNDERESTIMATED = 'underestimated'
const CONFIG_VALUE_PRICE_AREA_NORMAL = 'normal'
const CONFIG_VALUE_PRICE_AREA_GREEDY = 'greedy'

const Container = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const [tableData, setTableData] = useState([]);

  const [canaryStatus, setCanaryStatus] = useState(CONFIG_VALUE_CANARY_STATUS_OFFLINE);
  const [canaryPercent, setCanaryPercent] = useState(50);
  const [modeModalOpen, setModeModalOpen] = useState(false);
  const [radioValue, setRadioValue] = useState('canary');

  const handleChangeRadio = (e) => {
    setRadioValue(e.target.value)
  }

  const [submitData, setSubmitData] = useState({
    version: undefined,
    memo: '',
    canary_percentage: 10
  });

  const [modalTitle, setModalTitle] = useState('创建灰度版本');

  const [modalMode, setModalMode] = useState('POST');

  const [openModal, setOpenModal] = useState(false);

  const handleClickPostCanary = () => {
    setModalMode('POST')
    setModalTitle('创建灰度版本')
    setSubmitData({
      version: undefined,
      memo: '',
      canary_percentage: 10
    })
    setOpenModal(true)
  }

  const handleModeModalSubmit = () => {
    return canaryService.put('/canary/status', {
      status: radioValue
    }).then((res) => {
      setModeModalOpen(false)
      ref.current.success('修改成功')
      fetchStatus(tableData)
    })
  }

  const handleModalSubmit = () => {
    if (modalMode === 'POST') {
      return handleCreateModalSubmit()
    } else {
      return handleEditModalSubmit()
    }
  }

  const handleCreateModalSubmit = () => {
    return canaryService.post('/canary', submitData).then((res) => {
      ref.current.success('创建成功')
      refreshTable().then((tableData) => fetchStatus(tableData))
    })
  }

  const handleEditModalSubmit = () => {
    return canaryService.patch('/canary', submitData).then((res) => {
      ref.current.success('修改成功')
      refreshTable().then((tableData) => fetchStatus(tableData))
    })
  }

  const handleTableEdit = (version, canary_percentage, memo) => {
    setSubmitData({
      version: version,
      canary_percentage: canary_percentage,
      memo: memo
    })
    console.log(submitData)
    setModalMode('PATCH')
    setModalTitle(`修改灰度版本 V${version}`)
    setOpenModal(true)
  }



  const handleCanaryPercentChange = (value) => {
    setSubmitData({
      ...submitData,
      canary_percentage: value
    })
  }

  const handleMemoChange = (e) => {
    setSubmitData({
      ...submitData,
      memo: e.target.value
    })
  }

  const onChangeSwitch = (value) => {
    if (value === false) {
      setModeModalOpen(true)
    } else {
      setModeModalOpen(true)
    }

  }

  const refreshTable = () => {
    return canaryService.get('/canary/list').then((result) => {
      setTableData(
        transferCanaryList(result.data.data)
      )
      return transferCanaryList(result.data.data)
    }).catch((err) => {

    });
  }


  useEffect(() => {
    refreshTable().then((tableData) => fetchStatus(tableData))

    return () => {

    }
  }, [])



  return (
        <>
          <Breadcrumb
            style={{
              margin: '16px 0',
            }}
          >
            <Breadcrumb.Item>定期投资</Breadcrumb.Item>
          </Breadcrumb>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
            }}
          >
            <div>
              <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                <h3>当前状态</h3>
                <Row justify="center">
                  <Col>

                  </Col>
                </Row>
                <h3>投资记录列表</h3>
                <Button onClick={handleClickPostCanary}>新增投资记录</Button>
                <AipListTable data={tableData} onClick={handleTableEdit}></AipListTable>
              </Space>
            </div>
          </div>

          <Modal
            title={modalTitle}
            open={openModal}
            handleCloseModal={() => setOpenModal(false)}
            handleOk={handleModalSubmit}
          >
            <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
              <h3>灰度流量百分比</h3>
              <CanarySlider
                value={submitData['canary_percentage']}
                handleChange={handleCanaryPercentChange}
              ></CanarySlider>
              <h3>备注</h3>
              {/* <CanarySlider
                value={submitData['memo']}
                handleChange={handleMemoChange}
              ></CanarySlider> */}

              <Input
                // style={{
                //   margin: '0 16px',
                // }}
                value={submitData['memo']}
                onChange={handleMemoChange}
              />
            </Space>
          </Modal>
          <Message ref={ref}></Message>
        </>
  );
};


export default Container;



