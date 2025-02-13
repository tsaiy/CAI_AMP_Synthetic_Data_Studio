import get from 'lodash/get';
import { Col, Row, Tabs } from 'antd';
import { Evaluation, EvaluationDetails } from '../Evaluator/types';
import styled from 'styled-components';
import { getTopicMap } from '../Evaluator/util';
import EvaluateTopicTable from '../Evaluator/EvaluateTopicTable';


interface Props {
    evaluation: Evaluation;
    evaluationDetails: EvaluationDetails;
}

const Container = styled.div`  
   padding: 16px;
   background-color: #ffffff;
`;

const EvaluationGenerationTab: React.FC<Props> = ({ evaluation, evaluationDetails }) => { 
    console.log('--------EvaluationGenerationTab', evaluation, evaluationDetails);  
    const result = get(evaluationDetails, 'evaluation');
    console.log('result', result);
    

    let topicTabs: any[] = [];
    const { topics, topicMap } = getTopicMap({ result });
    console.log('topicMap',  topicMap);
    console.log('topics',  topics);
    topicTabs = topics.map((topicName: string, index: number) => ({
      key: `${topicName}-${index}`,
      label: topicName,
      value: topicName,
      children: <EvaluateTopicTable data={get(topicMap, `${topicName}.evaluated_pairs`, [])} topicResult={get(topicMap, `${topicName}`)} topic={topicName} />
    }));
    console.log('topicTabs', topicTabs);


    return (
        <Container>
            <Row>
                <Col sm={24}>
                    <Tabs tabPosition="left" items={topicTabs}/>
                </Col>
            </Row>
        </Container>
    );
}

export default EvaluationGenerationTab;