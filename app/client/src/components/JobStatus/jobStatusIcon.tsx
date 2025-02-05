import { Tooltip } from "antd";
import { JobStatus } from "../../types";
import StatusInProgress from '@cloudera-internal/cuix-core/icons/react/StatusInProgressIcon';
import StatusSuccessIcon from '@cloudera-internal/cuix-core/icons/react/StatusSuccessIcon';
import StatusErrorIcon from '@cloudera-internal/cuix-core/icons/react/StatusErrorIcon';
import InfoIcon from '@cloudera-internal/cuix-core/icons/react/InfoIcon';

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
                return <Tooltip title={tooltipTitles.ENGINE_SUCCEEDED}><StatusSuccessIcon /></Tooltip>;
            case 'ENGINE_STOPPED':
                return <Tooltip title={tooltipTitles.ENGINE_STOPPED}><StatusErrorIcon /></Tooltip>;
            case 'ENGINE_TIMEDOUT':
                return <Tooltip title={tooltipTitles.ENGINE_TIMEDOUT}><StatusErrorIcon /></Tooltip>;
            case 'ENGINE_SCHEDULING':
                return <Tooltip title={tooltipTitles.ENGINE_SCHEDULING}><StatusInProgress /></Tooltip>;
            case 'ENGINE_RUNNING':
                return <Tooltip title={tooltipTitles.ENGINE_RUNNING}><StatusInProgress /></Tooltip>;
            case null:
                return <Tooltip title={tooltipTitles.null}><StatusSuccessIcon /></Tooltip>;
            default:
                return <Tooltip title={tooltipTitles.default}><InfoIcon /></Tooltip>;
        }
    }

    return jobStatus();
}