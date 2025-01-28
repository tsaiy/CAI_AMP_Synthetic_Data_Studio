import Layout from 'antd/es/layout';
import { ConfigProvider, Flex, Menu, notification, Typography } from 'antd';
import type { MenuProps } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';
import styled from 'styled-components';

import './App.css'
import clouderaIcon from './assets/ic-cloudera-sm.svg';
import clouderaText from './assets/logo-cloudera-white.svg'
import { LABELS } from './constants';
import { Pages } from './types';
import { QueryClient, QueryClientProvider } from 'react-query';
import React, { useMemo } from 'react';

const { Header, Content } = Layout;
type MenuItem = Required<MenuProps>['items'][number];
const queryClient = new QueryClient()

const AppContainer = styled(Layout)`
  height: 100%;
`
const AppContent = styled(Content)`
  height: 100%;
  padding: 12px 24px;
`
const BrandingContainer = styled(Flex)`
  padding: 10px;
`
const BrandingTitle = styled(Typography)`
  color: white;
  font-size: 16;
`
const BrandingTextContainer = styled(Flex)`
  padding-top: 5px;
`
const PageHeader = styled(Header)`
  height: fit-content;
  padding: 5px 15px
`;
const StyledImg = styled.img`
  height: ${props => props?.height && `${props.height}px`}
`

const pages: MenuItem[] = [
  {
    key: Pages.HOME,
    label: (
      <Link to={`${Pages.HOME}`}>{LABELS[Pages.HOME]}</Link>
    ),
  },
  {
    key: Pages.GENERATOR,
    label: (
      <Link to={`${Pages.GENERATOR}`}>{LABELS[Pages.GENERATOR]}</Link>
    ),
  },
  {
    key: Pages.HISTORY,
    label: (
      <Link to={`${Pages.HISTORY}`}>{LABELS[Pages.HISTORY]}</Link>
    ),
  },
]

const NotificationContext = React.createContext({messagePlacement: 'topRight'});

const Container = () => {
  const location = useLocation();
  const notificationContextValue = useMemo(() => ({ messagePlacement: 'topRight' }), []);

  return (
    <ConfigProvider theme={{
      components: {
        List: {
          emptyTextPadding: 0
        }
      }
    }}>
      <QueryClientProvider client={queryClient}>
        <NotificationContext.Provider value={notificationContextValue}>
          <AppContainer>
            <PageHeader>
              <Flex justify='space-between' align='center'>
                <BrandingContainer gap={5}>
                  <StyledImg src={clouderaIcon} height={48} />
                  <BrandingTextContainer align='start' justify='center' vertical>
                    <img src={clouderaText} height={12} />
                    <BrandingTitle>{'Synthetic Data Studio'}</BrandingTitle>
                  </BrandingTextContainer>
                </BrandingContainer>
                <Menu
                  disabledOverflow={true}
                  items={pages}
                  mode="horizontal"
                  // onClick={handleMenuClick}
                  selectable={false}
                  selectedKeys={[location.pathname]}
                  theme="dark"
                  defaultSelectedKeys={[Pages.GENERATOR]} />
              </Flex>
            </PageHeader>
            <AppContent>
              <div style={{ height: "100%" }} key={location.pathname}>
                <Outlet />
              </div>
            </AppContent>
          </AppContainer>
        </NotificationContext.Provider>
      </QueryClientProvider>
    </ConfigProvider>
  )
};

export default Container;