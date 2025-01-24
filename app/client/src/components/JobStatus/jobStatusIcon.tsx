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
                return <CheckCircleTwoTone twoToneColor="#52c41a" />;
            case 'ENGINE_STOPPED':
            case 'ENGINE_TIMEDOUT':
                return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
            case 'ENGINE_SCHEDULING':
            case 'ENGINE_RUNNING':
                return <LoadingOutlined spin />;
            default:
                return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
        }
    }

    return (
        <>
            {jobStatus()}
        </>
    )
}