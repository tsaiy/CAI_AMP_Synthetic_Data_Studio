import { Col, Row } from "antd";
import { Dataset } from "../Evaluator/types";
import CustomGenerationTable from "./CustomGenerationTable";
import DatasetGenerationTopics from "./DatasetGenerationTopics";
import { CustomResult } from "../DataGenerator/types";
import { isEmpty } from "lodash";
import { DatasetDetails, DatasetGeneration } from "../Home/types";
import styled from "styled-components";



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
    const hasCustomSeeds = !Array.isArray(datasetDetails?.generation);
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

