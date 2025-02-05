import get from 'lodash/get';
import isString from 'lodash/isString';
import isObject from 'lodash/isObject';
import { Badge, Col, Flex, Row, Table } from 'antd';
import { EvaluatedPair, TopicEvaluationResult } from './types';
import styled from 'styled-components';
import { SyntheticEvent, useState } from 'react';
import GeneratedEvaluationModal from './GeneratedEvaluationModal';
import { getColorCode } from './util';

interface Props {
  topic: string;  
  data: EvaluatedPair[]; 
  topicResult: TopicEvaluationResult;   
}

const StyledFlex = styled(Flex)`
  .label {
    height: 28px;
    flex-grow: 0;
    font-size: 20px;
    font-weight: 300;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.4;
    letter-spacing: normal;
    text-align: left;
    color: #1b2329;
    margin-bottom: 10px;
  }
  .value {
    margin-left: 6px;
    height: 28px;
    flex-grow: 0;
    font-size: 20px;
    font-weight: 300;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.4;
    letter-spacing: normal;
    text-align: left;
    color: #1b2329;
  }  
`;

const StyledTable = styled(Table)`
  .ant-table-row {
    cursor: pointer;
  }
`


const EvaluateTopicTable: React.FC<Props> = ({ data, topic, topicResult }) => {
    console.log('EvaluateTopicTable > ', data, topic, topicResult);
    const [displayRecord, setDisplayRecord] = useState<EvaluatedPair | null>(null);
    const [showModal, setShowModal] = useState(false);
    const average_score = get(topicResult, 'average_score', 0);
    const colummns = [
        {
            title: 'Prompt',
            dataIndex: 'question',
            ellipsis: true,
            render: (question: string) => <>{question}</>
        },
        {
            title: 'Completion',
            dataIndex: 'solution',
            ellipsis: true,
            render: (solution: string) => <>{solution}</>
        },
        {
            title: 'Justification',
            ellipsis: true,
            render: (pair: EvaluatedPair) => {
              console.log('pair', pair);
              const justification = get(pair, 'evaluation.justification', 0);
              if (isString(justification)) {
                return <>{justification}</>;
              }
              if (isObject(justification)) {
                return <>{JSON.stringify(justification)}</>;
              }
              return 'N/A';
            } 
        },
        {
            title: 'Score',
            ellipsis: true,
            width: 100,
            render: (pair: EvaluatedPair) => {
             const count = get(pair, 'evaluation.score', 0);
             return <Badge count={count} color={getColorCode(count)} showZero />
            } 
        }
    ];

    const onRowClick = (event: SyntheticEvent, record: EvaluatedPair) => {
      event.stopPropagation();
      setDisplayRecord(record);
      setShowModal(true);
    }


    return (
        <>
          <Row style={{ marginBottom: '16px' }}>
            <Col sm={24}>
              <StyledFlex>
                <div className="label">Average Score</div>
                <div className="value">{average_score}</div>
              </StyledFlex>
            </Col>
          </Row>
       
        <StyledTable
            columns={colummns}
            dataSource={data}
            pagination={{ defaultPageSize: 10, showSizeChanger: true, pageSizeOptions: ['5', '10', '20']}}
            rowKey={(_record, index) => `evaluate-topic-${topic}-${index}`}
            onRow={(record) => {
                return {
                  onClick: (event) => onRowClick(event, record)
                };
              }}
        />
        {showModal && 
          <GeneratedEvaluationModal 
            evaluatedPair={displayRecord as EvaluatedPair} 
            onClose={() => setShowModal(false)} 
        />}
         </>
    )
};

export default EvaluateTopicTable;