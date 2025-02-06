import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import { Col, Row, Tabs } from 'antd';
import { Dataset, Evaluation, EvaluationDetails } from '../Evaluator/types';
import styled from 'styled-components';
import { getTopicMap } from '../Evaluator/util';
import EvaluateTopicTable from '../Evaluator/EvaluateTopicTable';


interface Props {
    dataset: Dataset
    evaluation: Evaluation;
    evaluationDetails: EvaluationDetails;
}

const Container = styled.div`  
   padding: 16px;
   background-color: #ffffff;
`;

const EvaluationGenerationTab: React.FC<Props> = ({ dataset, evaluation, evaluationDetails }) => { 
    console.log('--------EvaluationGenerationTab', evaluation, evaluationDetails);  
    const result = get(evaluationDetails, 'evaluation');
    console.log('result', result);


    let topicTabs: any[] = [];
    const { topics, topicMap } = getTopicMap({ result });
    console.log('topicMap',  topicMap);
    console.log('topics',  topics);
    if (dataset.topics !== null && !isEmpty(dataset.topics)) {
        topicTabs = topics.map((topicName: string, index: number) => ({
            key: `${topicName}-${index}`,
            label: topicName,
            value: topicName,
            children: <EvaluateTopicTable data={get(topicMap, `${topicName}.evaluated_pairs`, [])} topicResult={get(topicMap, `${topicName}`)} topic={topicName} />
        }));
    }
   
    console.log('topicTabs', topicTabs);
    if (isEmpty(topicTabs)) {
        const values = Object.values(topicMap);
        return (
            <Row>
                <Col sm={24}>
                    <EvaluateTopicTable data={get(values, `[0].evaluated_pairs`, [])} topicResult={get(values, '[0]')} topic={'Evaluate'} />
                </Col>
            </Row>
        );
    }


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