import isEmpty from 'lodash/isEmpty';
import { Alert, Button, Flex, Modal, Spin, Typography } from 'antd';
import React, { useEffect } from 'react';
import { useUpgradeStatus, useUpgradeSynthesisStudio } from './hooks';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;


const UpgradeButton: React.FC = () => {
    const [showModal, setShowModal] = React.useState(false);
    const [loading, setLoading] = React.useState(false);
    const [enableUpgrade, setEnableUpgrade] = React.useState(false);
    const { data, isError } = useUpgradeStatus();
    const { upgradeStudio, isLoading } = useUpgradeSynthesisStudio();
    console.log("Upgrade data", data);

    useEffect(() => {       
        if (!isEmpty(data)) {
            setEnableUpgrade(data?.updates_available);
        }
    },[data, isLoading, isError]);

    const onClick = () => setShowModal(true);
    

    if (!enableUpgrade) {
        return null;
    }
    console.log("Upgrade available", enableUpgrade);

    const onFinish = async () => {
        // logic to handle upgrade
        upgradeStudio();
        setLoading(true);
    }

    return (
        <> 
        {enableUpgrade && <Button type="text" style={{ paddingLeft: 0 }} onClick={onClick}>
            <span style={{ color: 'rgba(255, 255, 255, 0.65)'}}>Upgrade</span>
        </Button>}
        {showModal && (
            <Modal
                visible={showModal}
                okText={`Upgrade`}
                title={`Upgrade Synthesis Studio`}
                onCancel={() => setShowModal(false)}
                onOk={() => onFinish()}
                okButtonProps={{disabled: loading}}
                width={550}>
                <Text>
                    {`Are you sure you want to upgrade Synthesis Studio?`}
                </Text>
                <Alert
                    message="Upgrade in progress"
                    description="Please wait while we upgrade Synthesis Studio."
                    type="warning"
                    showIcon
                    style={{ marginTop: 16 }}
                /> 
                {loading && 
                    <Flex align="center" gap="middle">
                        <Spin indicator={<LoadingOutlined spin />} fullscreen />  
                    </Flex>}
          </Modal>
        )}
        </>
        
    )

}

export default UpgradeButton;
