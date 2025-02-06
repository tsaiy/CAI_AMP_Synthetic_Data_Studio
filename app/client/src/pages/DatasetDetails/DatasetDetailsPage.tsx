import get from 'lodash/get';
import { Card, Col, Flex, Layout, Row, Typography } from "antd";
import styled from "styled-components";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import { useParams } from "react-router-dom";
import { useGetDatasetDetails } from "./hooks";
import Loading from "../Evaluator/Loading";


const { Content } = Layout;
const { Title } = Typography;


const StyledHeader = styled.div`
  height: 28px;
  flex-grow: 0;
  font-family: Roboto;
  font-size: 20px;
  font-weight: 300;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.4;
  letter-spacing: normal;
  text-align: left;
`;

const StyledLabel = styled.div`
  margin-bottom: 4px;
  font-family: Roboto;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
`;

const StyledContent = styled(Content)`
  background-color: #ffffff;
  margin: 24px;
  .ant-table {
    overflow-y: scroll;
  }
`;

const StyledLabel = styled.div`
  display: block;
  font-size: 12px;
  color: #5a656d;
`;

const StyledValue = styled.div`
    color: #1b2329;
    font-size: 12px;
    font-variant: tabular-nums;
    line-height: 1.4285;
    list-style: none;
    font-feature-settings: 'tnum';
`;


const DatasetDetailsPage: React.FC = () => {
    const { generate_file_name } = useParams();
    const { data, error, isLoading } = useGetDatasetDetails(generate_file_name as string);
    const dataset = get(data, 'dataset');
    const datasetDetails = get(data, 'datasetDetails');
    console.log('DatasetDetailsPage > dataset', dataset);
    console.log('DatasetDetailsPage > datasetDetails', datasetDetails);

    if (isLoading) {
        return (
          <StyledContent>
            <Loading />
          </StyledContent>
        );
      }


    return (
        <Layout>
            <StyledContent>
                <Card>
                    <Row>
                        <Col sm={22}>
                            <StyledHeader>{dataset?.display_name}</StyledHeader>
                        </Col>
                    </Row>
                    <Row>
                        <Col sm={5}>
                          <Flex vertical>
                            <StyledLabel>Model</StyledLabel>
                            <StyledValue>dataet?.model_id</StyledValue>
                          </Flex>
                        </Col>
                        <Col sm={5}>
                        <Flex vertical>
                            <StyledLabel>Model Provider</StyledLabel>
                            <StyledValue>dataet?.inference_type</StyledValue>
                          </Flex>
                        </Col>
                    </Row>
                </Card>    
            </StyledContent>
        </Layout>
        
    );
}

export default DatasetDetailsPage;