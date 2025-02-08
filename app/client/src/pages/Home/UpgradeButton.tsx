import isEmpty from 'lodash/isEmpty';
import { Button } from 'antd';
import React, { useEffect } from 'react';
import { useUpgradeStatus } from './hooks';




const UpgradeButton: React.FC = () => {
    const [showModal, setShowModal] = React.useState(false);
    const [enableUpgrade, setEnableUpgrade] = React.useState(false);
    const { data, isLoading, isError } = useUpgradeStatus();

    useEffect(() => {       
        if (isEmpty(data)) {
            setEnableUpgrade(data?.updates_available);
        }
    },[data, isLoading, isError]);

    const onUpgrade = () => {
        // Logic to handle upgrade
        console.log("Upgrading...");
    }

    if (!enableUpgrade) {
        return null;
    }

    return (
        <Button onClick={onUpgrade}>Upgrade</Button>
    )

}

export default UpgradeButton;
