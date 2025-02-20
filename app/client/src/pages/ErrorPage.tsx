import { Alert, Layout } from "antd";
import get from "lodash/get";
import { useRouteError } from "react-router-dom";
import styled from "styled-components";

const { Content } = Layout;

const StyledContent = styled(Content)`
    padding: 24px;
    background-color: #f5f7f8;
    margin: auto;
`;


const ErrorPage: React.FC = () => {
    const error = useRouteError();
    console.error('error', error);
    const message = get(error, 'message');

    return (
        <Layout>
            <StyledContent>
                <Alert
                    message="Error"
                    description={message || 'Fatal error occured during rendering the page'}
                    type="error"
                    showIcon
                />
            </StyledContent>
        </Layout>    
    );
}

export default ErrorPage;