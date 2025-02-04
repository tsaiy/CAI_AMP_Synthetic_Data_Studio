import { Tooltip } from "antd";
import { CheckCircleTwoTone, ExclamationCircleTwoTone, InfoCircleTwoTone, LoadingOutlined } from '@ant-design/icons';
import { JobStatus } from "../../types";

export type JobStatusProps = {
    status: JobStatus
    customTooltipTitles?: Partial<Record<JobStatus, string>>
}

const defaultTooltipTitles: Record<JobStatus, string> = {
    'ENGINE_SUCCEEDED': 'Success!',
    'ENGINE_STOPPED': 'Error!',
    'ENGINE_TIMEDOUT': 'Job timeout!',
    'ENGINE_SCHEDULING': 'Scheduling!',
    'ENGINE_RUNNING': 'Engine running!',
    'default': 'Check the job in the application!',
    'null': 'No job was executed'
}

export default function JobStatusIcon({ status, customTooltipTitles }: JobStatusProps) {
    const tooltipTitles = {...defaultTooltipTitles, ...customTooltipTitles};

    function jobStatus() {
        switch (status) {
            case "ENGINE_SUCCEEDED":
                return <Tooltip title={tooltipTitles.ENGINE_SUCCEEDED}><CheckCircleTwoTone twoToneColor="#52c41a" /></Tooltip>;
            case 'ENGINE_STOPPED':
                return <Tooltip title={tooltipTitles.ENGINE_STOPPED}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
            case 'ENGINE_TIMEDOUT':
                return <Tooltip title={tooltipTitles.ENGINE_TIMEDOUT}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
            case 'ENGINE_SCHEDULING':
                return <Tooltip title={tooltipTitles.ENGINE_SCHEDULING}><LoadingOutlined spin/></Tooltip>;
            case 'ENGINE_RUNNING':
                return <Tooltip title={tooltipTitles.ENGINE_RUNNING}><LoadingOutlined spin /></Tooltip>;
            case null:
                return <Tooltip title={tooltipTitles.null}><CheckCircleTwoTone twoToneColor="#52c41a" /></Tooltip>;
            default:
                return <Tooltip title={tooltipTitles.default}><InfoCircleTwoTone /></Tooltip>;
        }
    }

    return jobStatus();
}