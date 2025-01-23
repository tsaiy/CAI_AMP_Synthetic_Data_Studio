import { Button, Table, TableProps } from 'antd';
import React from 'react';
import DateTime from '../../components/DateTime/DateTime';
import { useGetExportJobs } from '../../api/Export/export';

const columns: TableProps<string>['columns'] = [
    {
        key: 'display_name',
        title: 'Source Dataset',
        dataIndex: 'display_name',
    }, {
        key: 'model_id',
        title: 'Export Name',
        dataIndex: 'model_id',
    }, {
        key: 'export_location',
        title: 'Export Location',
        dataIndex: 'average_score',
    }, {
        key: 'timestamp',
        title: 'Create Time',
        dataIndex: 'timestamp',
        render: (timestamp) => <DateTime dateTime={timestamp}></DateTime>

    }, {
        key: 'action',
        title: 'Actions',
        render: () =>
            <Button> Export menu item</Button>

    },
];

const ExportsTab: React.FC = () => {
    const { isLoading, isError, data, error } = useGetExportJobs();

    return (
        <>
            <Table<string>
                columns={columns}
                loading={isLoading}
                expandable={{
                    expandedRowRender: (exportedDataset) => <p style={{ margin: 0 }}>{exportedDataset.exportType}</p>,
                    rowExpandable: () => false,
                }}
                dataSource={data?.jobs || []}
            />
        </>
    );
};

export default ExportsTab;