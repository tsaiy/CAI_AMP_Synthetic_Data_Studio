import React from 'react';
import { CustomResult } from './types';
import { Table } from 'antd';

interface Props {
    results: CustomResult[]
}


const CustomResultTable: React.FC<Props> = ({ results }) => {

    const columns = [
        {
            title: 'Question',
            key: 'question',
            dataIndex: 'question',
            ellipsis: true,
            render: (question: string) => <>{question}</>
        },
        {
            title: 'Solution',
            key: 'solution',
            dataIndex: 'solution',
            ellipsis: true,
            render: (solution: string) => <>{solution}</>
        }
    ];

    return (
        <Table
            columns={columns}
            dataSource={results}
            rowClassName={() => 'hover-pointer'}
            rowKey={(_record, index) => `examples-table-${index}`}
            pagination={{
                showSizeChanger: true,
                showQuickJumper: false,
                hideOnSinglePage: true
            }}
        />    
    )
}

export default CustomResultTable;
