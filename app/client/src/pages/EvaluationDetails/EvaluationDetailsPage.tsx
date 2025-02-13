import get from 'lodash/get';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Badge, Button, Card, Col, Flex, Layout, Row, Tabs, TabsProps } from 'antd';
import styled from 'styled-components';
import {
    ArrowLeftOutlined
  } from '@ant-design/icons';
import { useGetEvaluationDetails } from './hooks';
import Loading from '../Evaluator/Loading';
import { getModelProvider, getUsecaseType } from '../DataGenerator/constants';
import { getColorCode } from '../Evaluator/util';
import { Evaluation } from '../Evaluator/types';
import EvaluationConfigurationTab from './EvaluationConfigurationTab';
import EvaluationGenerationTab from './EvaluationGenerationTab';


const { Content } = Layout;

const StyledContent = styled(Content)`
  // background-color: #ffffff;
  margin: 24px;
  .ant-table {
    overflow-y: scroll;
  }
`;

const StyledLabel = styled.div`
  margin-bottom: 4px;
  font-family: Roboto, -apple-system, 'Segoe UI', sans-serif;
  font-weight: 500;
  margin-bottom: 4px;
  display: block;
  font-size: 14px;
  color: #5a656d;
`;

const StyledValue = styled.div`
    // color: #1b2329;
    color: #5a656d;
    font-family: Roboto, -apple-system, 'Segoe UI', sans-serif;
    font-size: 12px;
    font-variant: tabular-nums;
    line-height: 1.4285;
    list-style: none;
    font-feature-settings: 'tnum';
`;


const StyledPageHeader = styled.div`
    height: 28px;
    align-self: stretch;
    flex-grow: 0;
    font-family: Roboto, -apple-system, 'Segoe UI', sans-serif;
    font-size: 20px;
    // font-weight: 600;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.4;
    letter-spacing: normal;
    text-align: left;
    color: rgba(0, 0, 0, 0.88);
`;

const StyledButton = styled(Button)`  
    padding-left: 0;
`

enum ViewType {
    CONFIURATION = 'configuration',
    GENERATION = 'generation',
  }  



const EvaluationDetailsPage: React.FC = () => {
    const { evaluate_file_name } = useParams();
    const [tabViewType, setTabViewType] = useState<ViewType>(ViewType.GENERATION);
    const { data, error, isLoading } = useGetEvaluationDetails(evaluate_file_name as string);
    console.log('data:', data,  error, isLoading);
    const evaluation = get(data, 'evaluation');
    const evaluationDetails = get(data, 'evaluationDetails');
    
    if (isLoading) {
        return (
          <StyledContent>
            <Loading />
          </StyledContent>
        );
    }


    const items: TabsProps['items'] = [
        {
            key: ViewType.GENERATION,
            label: 'Generation',
            children: <EvaluationGenerationTab  evaluation={evaluation as Evaluation} evaluationDetails={evaluationDetails}/>,
        },
        {
            key: ViewType.CONFIURATION,
            label: 'Parameter & Examples',
            children: <EvaluationConfigurationTab evaluation={evaluation} evaluationDetails={evaluationDetails} />,
        },
    ];
    console.log('tabViewType', tabViewType);


    const onTabChange = (key: string) =>
        setTabViewType(key as ViewType);

    return (
        <Layout>
        <StyledContent>
            <Row>
              <Col sm={24}>
                <StyledButton type="link" onClick={() => window.history.back()} style={{ color: '#1677ff' }} icon={<ArrowLeftOutlined />}>
                  Back to Home
                </StyledButton>
              </Col>
            </Row>
            <Row style={{ marginBottom: '16px', marginTop: '16px'  }}>
              <Col sm={20}>
                <StyledPageHeader>{evaluation?.display_name}</StyledPageHeader>
              </Col>
              {/* <Col sm={4}>
                <Flex style={{ flexDirection: 'row-reverse' }}>
                  <Dropdown menu={{ items: menuActions }}>
                    <Button onClick={(e) => e.preventDefault()}>
                      <Space>
                          Actions
                          <DownOutlined />
                      </Space>
                    </Button>
                  </Dropdown>
                </Flex>
              </Col> */}

            </Row>
            <Card>
                <Row>
                    <Col sm={8}>
                      <Flex vertical>
                        <StyledLabel>Model ID</StyledLabel>
                        <StyledValue>{evaluation?.model_id}</StyledValue>
                      </Flex>
                    </Col>
                    <Col sm={8}>
                      <Flex vertical>
                        <StyledLabel>Model Provider</StyledLabel>
                        <StyledValue>{getModelProvider(evaluation?.inference_type)}</StyledValue>
                      </Flex>
                    </Col>
                </Row>
                <Row style={{ marginTop: '16px' }}>
                <Col sm={8}>
                    <Flex vertical>
                        <StyledLabel>Average Score</StyledLabel>
                        <StyledValue>
                            <Badge count={evaluation?.average_score} color={getColorCode(evaluation?.average_score)} showZero />
                        </StyledValue>
                    </Flex>
                </Col>
                <Col sm={8}>
                    <Flex vertical>
                        <StyledLabel>Template</StyledLabel>
                        <StyledValue>{getUsecaseType(evaluation?.use_case)}</StyledValue>
                    </Flex>
                </Col>
            </Row>
            </Card>
            <br/>
            <br/>
            <Row>
                <Col span={24}>
                    <Tabs
                        defaultActiveKey={tabViewType}
                        items={items}
                        onChange={onTabChange} />
                </Col>
            </Row>
        </StyledContent> 
        </Layout>       
    );
};

export default EvaluationDetailsPage;