import { Tooltip } from "antd";
import { JobStatus } from "../../types";
import { CheckCircleTwoTone, ExclamationCircleTwoTone, LoadingOutlined } from '@ant-design/icons';

export type JobStatusProps = {
    status: JobStatus
}

export default function JobStatusIcon({ status }: JobStatusProps) {
    function jobStatus() {
        switch (status) {
            case "succeeded":
                return <CheckCircleTwoTone twoToneColor="#52c41a" />;
            case 'stopped':
            case 'failed':
            case 'timedout':
                return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
            case 'starting':
            case 'running':
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