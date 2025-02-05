import { Col, Flex, Layout, Row } from 'antd';
import React from 'react';
import styled from 'styled-components';
import SDGIcon from '../../assets/sdg-landing.svg';


const { Content } = Layout;

const StyledContent = styled(Content)`
    padding: 24px;
    background-color: #f5f7f8;
`;

const LeftSection = styled.div`
    display: flex;
    flex-direction: column;
    padding: 24px;
    width: 50%;
    .section-title {
        color: #120046;
        font-size: 64px;
        font-weight: bold;
        height: 140px;
        align-self: stretch;
        flex-grow: 0;
        font-family: Roboto, -apple-system, 'Segoe UI', sans-serif;
        font-stretch: normal;
        font-style: normal;
        line-height: 1.1;
        letter-spacing: normal;
        text-align: left;
        margin-bottom: 32px;
    }
    .section-item-title {
        height: 24px;
        flex-grow: 0;
        font-family: Roboto;
        font-size: 16px;
        font-weight: normal;
        font-stretch: normal;
        font-style: normal;
        line-height: 1.5;
        letter-spacing: normal;
        text-align: center;
        color: #000;
    }    
`;

const RightSection = styled.div`
    width: 50%;
    padding: 24px;
`;    

const StyledImg = styled.img`
  height: 80vh;
`

const WelcomePage: React.FC = () => {

    return (
        <Layout>
            <StyledContent>
                <Row>
                    <Col sm={12}>
                    <LeftSection>
                        <div className="section-title ">Synthetic Data Generator</div>
                        <div>
                        Use synthetic data generation to generate and validate a dataset at a fraction of the time and cost for testing LLM systems.
                        </div>
                        <div>

                        </div>

                    </LeftSection>
                    </Col>
                    <Col sm={12}>
                    <RightSection>
                         <StyledImg src={SDGIcon} />
                    </RightSection>
                    </Col>
                </Row>
            </StyledContent>
        </Layout>        

    );
}

export default WelcomePage;
