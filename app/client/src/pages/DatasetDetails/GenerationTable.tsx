import { Card, Table } from "antd";
import { DatasetGeneration } from "../Home/types";

interface Props {
    generation: DatasetGeneration;
}


const GenerationTable: React.FC<Props> = ({ generation }) => {
    console.log('GenerationTable > generation', generation);

    const columns = [
        {
            title: 'Prompt',
            key: 'Prompt',
            dataIndex: 'Prompt',
            ellipsis: true,
            render: (prompt: string) => {
                console.log('prompt',  prompt);
                return <>{prompt}</>
            }
        },
        {
            title: 'Completion',
            key: 'Completion',
            dataIndex: 'Completion',
            ellipsis: true,
            render: (completion: string) => <>{completion}</>
        }
    ];

    return (
        <Card>

            <Table
                columns={columns}
                dataSource={data}
                rowClassName={() => 'hover-pointer'}
                rowKey={(_record, index) => `generation-table-${index}`}
                pagination={{
                    showSizeChanger: true,
                    showQuickJumper: false,
                    hideOnSinglePage: true
                }}
            /> 
        </Card>
    );
}

export default GenerationTable;