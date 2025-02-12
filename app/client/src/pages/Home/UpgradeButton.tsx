import isEmpty from 'lodash/isEmpty';
import { Alert, Button, Modal, Typography } from 'antd';
import React, { useEffect } from 'react';
import { useUpgradeStatus } from './hooks';

const { Text } = Typography;


const UpgradeButton: React.FC = () => {
    const [showModal, setShowModal] = React.useState(false);
    const [enableUpgrade, setEnableUpgrade] = React.useState(false);
    const { data, isLoading, isError } = useUpgradeStatus();

    useEffect(() => {       
        if (isEmpty(data)) {
            setEnableUpgrade(data?.updates_available);
        }
    },[data, isLoading, isError]);

    const onClick = () => {
        // Logic to handle upgrade
        console.log("Upgrading...");
    }

    if (!enableUpgrade) {
        return null;
    }

    const onFinish = async () => {
        // Logic to handle upgrade
        console.log("Upgrading...");
        setShowModal(false);
    }

    return (
        <> 
        {enableUpgrade && <Button onClick={onClick}>Upgrade</Button>}
        {showModal && (
            <Modal
                visible={showModal}
                okText={`Upgrade`}
                title={`Upgrade Synthesis Studio`}
                onCancel={() => setShowModal(false)}
                onOk={() => onFinish()}
                width={400}>
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
          </Modal>
        )}
        </>
        
    )

}

export default UpgradeButton;
