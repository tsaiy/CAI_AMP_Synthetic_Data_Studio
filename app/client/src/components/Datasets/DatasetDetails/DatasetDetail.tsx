import { Descriptions, Flex, Modal, Table, Typography } from "antd";
import styled from "styled-components";
import Markdown from "../../Markdown";
import { DatasetResponse } from "../../../api/Datasets/response";
import { QuestionSolution } from "../../../pages/DataGenerator/types";
import { MODEL_PARAMETER_LABELS, Usecases } from "../../../types";
import { Dataset } from "../../../pages/Evaluator/types";
import PCModalContent from "../../../pages/DataGenerator/PCModalContent";

const { Text, Title } = Typography;

const StyledTable = styled(Table)`
    .ant-table-row {
        cursor: pointer;
    }
`

const MarkdownWrapper = styled.div`
    border: 1px solid #d9d9d9;
    border-radius: 6px;
    padding: 4px 11px;
`;

export type DatasetDetailProps = {
    datasetDetails: DatasetResponse | Dataset;
}

export default function DatasetDetail({ datasetDetails }: DatasetDetailProps) {

    const exampleCols = [
        {
          title: 'Prompts',
          dataIndex: 'prompts',
          ellipsis: true,
          render: (_text: QuestionSolution, record: QuestionSolution) => <>{record.question}</>
        },
        {
          title: 'Completions',
          dataIndex: 'completions',
          ellipsis: true,
          render: (_text: QuestionSolution, record: QuestionSolution) => <>{record.solution}</>
        },
      ]

    return (
        <Flex vertical gap="middle">
            <Title level={4}>Model ID</Title>
            <Text type="secondary">{datasetDetails.model_id}</Text>

            <Title level={4}>{'Examples'}</Title>
            <StyledTable
                bordered
                columns={exampleCols}
                dataSource={datasetDetails.examples || []}
                pagination={false}
                onRow={(record,) => ({
                    onClick: () => Modal.info({
                        title: 'View Details',
                        content: <PCModalContent {...record} />,
                        icon: undefined,
                        maskClosable: true,
                        width: 1000
                    })
                })}
                rowKey={(_record, index) => `summary-examples-table-${index}`}
            />

            <Title level={4}>Model Parameters</Title>
            <Descriptions
                bordered
                colon
                column={1}
                size='small'
                style={{ maxWidth: 400 }}
                items={
                    datasetDetails?.model_parameters
                        ? Object
                            .keys(datasetDetails.model_parameters)
                            .map(modelParameterKey => ({
                                label: MODEL_PARAMETER_LABELS[modelParameterKey as ModelParameters],
                                children: datasetDetails.model_parameters[modelParameterKey as ModelParameters],
                            }))
                        : []}></Descriptions>

            {(datasetDetails.schema && datasetDetails.use_case === Usecases.TEXT2SQL) && (
                <div>
                    <Title level={4}>{'DB Schema'}</Title>
                    <MarkdownWrapper>
                        <Markdown text={datasetDetails.schema} />
                    </MarkdownWrapper>
                </div>
            )}

        </Flex>
    )
}