import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import React from 'react';
import { CustomResult } from './types';
import { Table } from 'antd';

interface SeedResult {
  [key: string] : CustomResult;  
}


interface Props {
    results: SeedResult[]
}


const SeedResultTable: React.FC<Props> = ({ results }) => {
    if (isEmpty(results)) {
        return null;
    }
    const seeds = Object.keys(results);
    const data = seeds.map((seed: string) => ({
        seed,
        question: get(results, `${seed}.question`),
        solution: get(results, `${seed}.solution`)
    }))

    const columns = [
        {
            title: 'Seed',
            key: 'seed',
            dataIndex: 'seed',
            ellipsis: true,
            render: (seed: string) => <>{seed}</>
        },
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
            dataSource={data}
            rowClassName={() => 'hover-pointer'}
            rowKey={(_record, index) => `seeds-table-${index}`}
            pagination={{
                showSizeChanger: true,
                showQuickJumper: false,
                hideOnSinglePage: true
            }}
        />    
    )
}

export default SeedResultTable;
