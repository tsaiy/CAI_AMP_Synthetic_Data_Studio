import { Table, TableProps } from 'antd';
import React from 'react';
import DateTime from '../../components/DateTime/DateTime';
import { useGetExportJobs } from '../../api/Export/export';
import { ExportResponse, JobStatus } from '../../api/Export/response';
import { CheckCircleTwoTone, ExclamationCircleTwoTone, LoadingOutlined } from '@ant-design/icons';


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
    }, {
        key: 'timestamp',
        title: 'Create Time',
        dataIndex: 'timestamp',
        render: (timestamp) => <DateTime dateTime={timestamp}></DateTime>

    },
    {
        key: 'job_status',
        title: 'Status',
        dataIndex: 'timestamp',
        render: (status: JobStatus) => {
            switch (status) {
                case "success":
                    return <CheckCircleTwoTone twoToneColor="#52c41a"/>;
                case 'failure':
                    return <ExclamationCircleTwoTone twoToneColor="#eb2f96"/>;
                case 'in progress':
                    return <LoadingOutlined spin/>;
                default:
                    return <LoadingOutlined spin/>;
            }
        }
    },
];

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