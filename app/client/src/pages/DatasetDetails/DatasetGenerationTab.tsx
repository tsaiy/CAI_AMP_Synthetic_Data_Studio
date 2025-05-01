import { Col, Row } from 'antd';
import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import styled from 'styled-components';
import { Dataset } from '../Evaluator/types';
import CustomGenerationTable from './CustomGenerationTable';
import DatasetGenerationTopics from './DatasetGenerationTopics';
import { CustomResult } from "../DataGenerator/types";
import { DatasetDetails, DatasetGeneration } from '../Home/types';



interface Props {
    dataset: Dataset;
    datasetDetails: DatasetDetails;
}

const Container = styled.div`  
   padding: 16px;
   background-color: #ffffff;
`;



const DatasetGenerationTab: React.FC<Props> = ({ dataset, datasetDetails }) => {
    console.log('datasetDetails', datasetDetails);
    console.log('dataset', dataset);
    const topics = get(dataset, 'topics', []);
    const hasCustomSeeds = !Array.isArray(datasetDetails?.generation) || isEmpty(topics) || topics !== null;

    return (
        <Container>
            <Row>
                <Col sm={24}>
                    {hasCustomSeeds && <CustomGenerationTable results={datasetDetails?.generation as unknown as DatasetGeneration[]} />}
                    {!hasCustomSeeds && <DatasetGenerationTopics data={datasetDetails?.generation} dataset={dataset} />}
                </Col>
            </Row>

        </Container>
    ); 
}

export default DatasetGenerationTab;

