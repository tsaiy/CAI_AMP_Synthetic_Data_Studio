import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import React from 'react';
import { Link } from 'react-router-dom';
import { Avatar, Button, Card, Flex, Layout, List, Tabs, Typography } from 'antd';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import GradingIcon from '@mui/icons-material/Grading';
import EvaluateTopicTable from './EvaluateTopicTable';
import { EVALUATOR_JOB_SUCCESS, getTopicMap } from './util';
import styled from 'styled-components';
import { getProjectJobsUrl } from './hooks';


const { Content } = Layout;
const { Title } = Typography;

interface Props {
  result: any;
  demo: boolean
}


export const EVALUATE_NEXT_STEPS = [
  {
      avatar: '',
      title: 'Review Evaluation',
      description: 'Review your dataset evaluation to ensure it properly fits your usecase.',
      icon: <GradingIcon/>
  }
];

const StyleContent = styled(Content)`
  margin: 24px;
`;


const EvaluatorSuccess: React.FC<Props> = ({ result }) => {
  console.log('result', result)
  const hasTopics = (result: any) => {
    return !Array.isArray(result?.results)
  }

  let topicTabs = null;
  if (isEmpty(get(result, 'job_id')) && isEmpty(get(result, 'job_name')) && !isEmpty(result) && hasTopics(result)) {
    const { topics, topicMap } = getTopicMap(result);
    topicTabs = topics.map((topicName: string, index: number) => ({
      key: `${topicName}-${index}`,
      label: topicName,
      value: topicName,
      children: <EvaluateTopicTable data={get(topicMap, `${topicName}.evaluated_pairs`, [])} topicResult={get(topicMap, `${topicName}`)} topic={topicName} />
    }));
  }

  return (
    <Layout>
      <StyleContent>
        <Title level={2}>
          <Flex align='center' gap={10}>
            <CheckCircleIcon style={{ color: '#178718' }}/>
            {'Success'}
          </Flex>
          </Title>
          {topicTabs === null &&
            (<Flex gap={20} vertical>
               <Typography>
                 {EVALUATOR_JOB_SUCCESS}
               </Typography>
               <Flex>
                 <Button type='primary' style={{ marginLeft: '4px', marginRight: '4px' }}>
                   <a href={getProjectJobsUrl()} target='_blank' rel='noreferrer'>
                     {'View Job'}
                   </a>
                 </Button>
               </Flex>
            </Flex>)}
           
          {topicTabs !== null && 
          <>
            <Typography>
              {'Your dataset evaluation was successfully generated. You can review your evaluation in the table below.'}
            </Typography>
            <Card title={'Generated Evaluations'} style={{ marginTop: '36px' }}>
              <Tabs tabPosition='left' items={topicTabs}/>
            </Card>
          </>}

          <Title level={2}>{'Next Steps'}</Title>
            <List
              itemLayout="horizontal"
              dataSource={EVALUATE_NEXT_STEPS}
              renderItem={(item, i) => (
                <List.Item key={`${item.title}-${i}`}>
                  <List.Item.Meta
                    avatar={<Avatar style={{ backgroundColor: '#1677ff'}} icon={item.icon} />}
                    title={item.title}
                    description={item.description}
                  />
                </List.Item>
                )}
            />
           
           <Flex style={{ marginTop: '24px' }}>
              <Button icon={<FormatListBulletedIcon/>}>
                <Link to={`/history`}>{'View Evaluation List'}</Link>
              </Button> 
           </Flex>   
      </StyleContent>
    </Layout>    
  );
}

export default EvaluatorSuccess;

