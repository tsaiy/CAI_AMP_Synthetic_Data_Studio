import { LoadingOutlined } from '@ant-design/icons';
import { Flex, Spin } from 'antd';
import styled from 'styled-components';

const StyledFlex = styled(Flex)`
  position: fixed;
  left: 40%;
  top: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
`

const Loading = () => (
  <StyledFlex align="center" gap="middle" style={{ width: '100%', height: '100%', margin: 'auto'}}>
    <Spin indicator={<LoadingOutlined spin style={{ fontSize: 48 }}/>} size="large" />
  </StyledFlex>
);

export default Loading;