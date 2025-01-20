import { FC } from 'react';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { Tooltip} from 'antd';
import styled from 'styled-components';

const HelpTooltipIcon = styled(QuestionCircleOutlined)`
    color: #1777ff;
    font-size: ({ size }) => size;
`

interface Props {
    message: string | undefined;
    size?: number;
}
const TooltipIcon: FC<Props> = ({ message, size = 16 }) => {
    return (
        <Tooltip title={message}>
            <HelpTooltipIcon style={{ fontSize: size }}/>
        </Tooltip>
    )
}

export default TooltipIcon