import { Flex, Table, TableProps, Tooltip, Typography } from 'antd';
import React from 'react';
import DateTime from '../../components/DateTime/DateTime';
import { useGetExportJobs } from '../../api/Export/export';
import { ExportResponse, JobStatus } from '../../api/Export/response';
import { CheckCircleTwoTone, ExclamationCircleTwoTone, LoadingOutlined } from '@ant-design/icons';
import { CDSW_PROJECT_URL } from '../../constants';

const { Link } = Typography;

const jobStatus = (status: JobStatus) => {
    switch (status) {
        case "success":
            return <CheckCircleTwoTone twoToneColor="#52c41a" />;
        case 'ENGINE_FAILED':
        case 'failure':
            return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
        case 'in progress':
            return <LoadingOutlined spin />;
        default:
            return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
    }
};

const columns: TableProps<ExportResponse>['columns'] = [
    {
        key: 'display_name',
        title: 'Source Dataset',
        dataIndex: 'display_name',
    }, {
        key: 'display_export_name',
        title: 'Export Name',
        dataIndex: 'display_export_name',
    }, {
        key: 'hf_export_path',
        title: 'Export Location',
        dataIndex: 'hf_export_path',
        render: (path) => <Link href={path} target="_blank">{path}</Link>
    }, {
        key: 'timestamp',
        title: 'Create Time',
        dataIndex: 'timestamp',
        render: (timestamp) => <DateTime dateTime={timestamp}></DateTime>
    },
    {
        key: 'job_id',
        title: 'Job ID',
        dataIndex: 'job_id',
        render: (jobId) => <Link href={`${CDSW_PROJECT_URL}/jobs/${jobId}`} target="_blank">{jobId}</Link>
    },
    {
        key: 'job_status',
        title: 'Status',
        dataIndex: 'timestamp',
        render: (status: JobStatus) => <Flex justify='center' align='center'>
            {jobStatus(status)}
        </Flex>
    },
];

// https://ai-workbench.eng-ml-l.vnu8-sqze.cloudera.site/kisslac/export-list-test-01/jobs/465

const ExportsTab: React.FC = () => {
    const { isLoading, isError, data, error } = useGetExportJobs();

    return (
        <>
            <Table<ExportResponse>
                rowKey={row => row.id}
                columns={columns}
                loading={isLoading}
                dataSource={data || []}
            />
        </>
    );
};

export default ExportsTab;