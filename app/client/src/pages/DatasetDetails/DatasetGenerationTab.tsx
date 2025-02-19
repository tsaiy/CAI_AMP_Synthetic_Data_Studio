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
    console.log(`DatasetGenerationTab > dataset`, dataset);
    console.log(` datasetDetails`, datasetDetails);
    const topics = get(dataset, 'topics', []);
    console.log(` topics`, topics);
    const hasCustomSeeds = !Array.isArray(datasetDetails?.generation) || isEmpty(topics) || topics !== null;
    console.log(` hasCustomSeeds`, hasCustomSeeds);

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

