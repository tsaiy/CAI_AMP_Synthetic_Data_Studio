import { Flex, Typography, Modal, Button, Descriptions, Table } from "antd";
import { EvaluationResponse } from "../../../api/Evaluations/response";
import { MODEL_PARAMETER_LABELS, ModelParameters } from "../../../types";
import styled from "styled-components";
import { JustificationScore } from "../../../pages/DataGenerator/types";
import ReactMarkdown from "react-markdown";
import ScoreJustificationModalContent from "./ScoreJustificationModalContent";
import { Evaluation } from "../../../pages/Home/types";

const { Title, Text } = Typography;

const StyledTable = styled(Table)`
    .ant-table-row {
        cursor: pointer;
    }
`

const StyledCustomPromptWrapper = styled.div`
    pre {
        overflow: auto;
    }
`

const exampleCols = [
  {
    title: 'Score',
    dataIndex: 'score',
    ellipsis: true,
    render: (_text: JustificationScore, record: JustificationScore) => <>{record.score}</>
  },
  {
    title: 'Justification',
    dataIndex: 'justification',
    ellipsis: true,
    render: (_text: JustificationScore, record: JustificationScore) => <>{record.justification}</>
  },
]

export type EvaluationDetailModalProps = {
  evaluationDetail: EvaluationResponse | Evaluation;
  isModalActive: boolean;
  setIsModalActive: (isActive: boolean) => void;
}

export default function EvaluationDetailModal({ isModalActive, setIsModalActive, evaluationDetail }: EvaluationDetailModalProps) {
  return (
    <Modal title={`View Evaluation Details`} width={"80%"} open={isModalActive} onCancel={() => setIsModalActive(false)} onClose={() => setIsModalActive(false)} footer={<Button type="primary" onClick={() => setIsModalActive(false)}>Ok</Button>}>
      <Flex vertical gap="middle">
        <Title level={4}>Model ID</Title>
        <Text type="secondary">{evaluationDetail.model_id}</Text>

        <Title level={4}>Model Parameters</Title>
        <Descriptions
          bordered
          colon
          column={1}
          size='small'
          style={{ maxWidth: 400 }}
          items={
            evaluationDetail?.model_parameters
              ? Object
                .keys(evaluationDetail.model_parameters)
                .map(modelParameterKey => ({
                  label: MODEL_PARAMETER_LABELS[modelParameterKey as ModelParameters],
                  children: evaluationDetail.model_parameters[modelParameterKey as ModelParameters],
                }))
              : []}></Descriptions>

        <Title level={4}>{'Prompt'}</Title>
        <StyledCustomPromptWrapper>
          <ReactMarkdown className={"evaluation-detail-prompt-markdown"} children={evaluationDetail.custom_prompt}></ReactMarkdown>
        </StyledCustomPromptWrapper>

        <Title level={4}>{'Examples'}</Title>
        <StyledTable
          bordered
          columns={exampleCols}
          dataSource={evaluationDetail.examples || []}
          pagination={false}
          onRow={(record,) => ({
            onClick: () => Modal.info({
              title: 'View Details',
              content: <ScoreJustificationModalContent {...record} />,
              icon: undefined,
              maskClosable: true,
              width: 1000
            })
          })}
          rowKey={(_record, index) => `summary-examples-table-${index}`}
        />

      </Flex>
    </Modal>
  )
}