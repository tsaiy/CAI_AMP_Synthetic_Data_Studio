import { Tooltip } from "antd";
import { JobStatus } from "../../types";
import { CheckCircleTwoTone, ExclamationCircleTwoTone, LoadingOutlined } from '@ant-design/icons';

export type JobStatusProps = {
    status: JobStatus
}

export default function JobStatusIcon({ status }: JobStatusProps) {
    function jobStatus() {
        switch (status) {
            case "ENGINE_SUCCEEDED":
                return <Tooltip title={`Successful export!`}><CheckCircleTwoTone twoToneColor="#52c41a" /></Tooltip>;
            case 'ENGINE_STOPPED':
            case 'ENGINE_TIMEDOUT':
                return <Tooltip title={`Error during job execution!`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
            case 'ENGINE_SCHEDULING':
            case 'ENGINE_RUNNING':
                return <Tooltip title={`Export is in progress!`}><LoadingOutlined spin /></Tooltip>;
            default:
                return <Tooltip title={`Error during job execution!`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
        }
    }

    return (
        <>
            {jobStatus()}
        </>
    )
}