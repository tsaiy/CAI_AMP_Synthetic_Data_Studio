import { Flex, Layout, Typography } from "antd";
import styled from "styled-components";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import { useParams } from "react-router-dom";
import { useGetDataset } from "../Evaluator/hooks";


const { Content } = Layout;
const { Title } = Typography;

const StyleContent = styled(Content)`
  margin: 24px;
`;


const DatasetDetailsPage: React.FC = () => {
    const { generate_file_name } = useParams();
    const { dataset, prompt, examples } = useGetDataset(generate_file_name as string);
    console.log('DatasetDetailsPage > dataset', dataset);

    return (
        <Layout>
            <StyleContent>
                <Title level={2}>
                    <Flex align='center' gap={10}>
                        <CheckCircleIcon style={{ color: '#178718' }}/>
                        {'Success'}
                    </Flex>
                </Title>
            </StyleContent>  
        </Layout>
        
    );
}

export default DatasetDetailsPage;