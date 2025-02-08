import React from 'react';

import { Table } from 'antd';
import { CustomResult } from '../DataGenerator/types';
import { DatasetGeneration } from '../Home/types';

interface Props {
    results: DatasetGeneration[]
}


const CustomGenerationTable: React.FC<Props> = ({ results }) => {

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
            rowKey={(_record, index) => `generation-table-${index}`}
            pagination={{
                showSizeChanger: true,
                showQuickJumper: false,
                hideOnSinglePage: true
            }}
        />    
    )
}

export default CustomGenerationTable;
