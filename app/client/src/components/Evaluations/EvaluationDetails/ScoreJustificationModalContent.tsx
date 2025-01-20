import { Flex, Typography } from 'antd';
import styled from 'styled-components';

import TooltipIcon from '../../TooltipIcon';
import Markdown from '../../Markdown';

const { Title } = Typography;
const Container = styled(Flex)`
    margin-top: 15px
`
const StyledTitle = styled(Title)`
    margin-top: 0;
    margin-bottom: 0 !important;
`;
const TitleGroup = styled(Flex)`
    margin-top: 10px;
    margin-bottom: 10px;
`

/**
 * Modal Content for prompts and completions
 */
const ScoreJustificationModalContent = ({ justification = '', score = 0 }) => {
    return (
        <Container gap={10} vertical>
            {justification && (
                <div>
                    <TitleGroup align='center' gap={5}>
                        <StyledTitle level={5}>{'Justification'}</StyledTitle>
                        <TooltipIcon message={'Justification on the result'} size={14} />
                    </TitleGroup>
                    <Markdown text={justification} />
                </div>
            )}
            {score && (
                <div>
                    <TitleGroup align='center' gap={5}>
                        <StyledTitle level={5}>{'Score'}</StyledTitle>
                        <TooltipIcon message={'Score of the result'} size={14} />
                    </TitleGroup>
                    <Markdown text={score.toString()} />
                </div>
            )}
        </Container>
    )
}

export default ScoreJustificationModalContent;