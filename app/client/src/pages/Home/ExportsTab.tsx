import { Button, Col, Flex, Row, Table, TableProps, Tooltip, Typography } from 'antd';
import React from 'react';
import DateTime from '../../components/DateTime/DateTime';
import { useGetExportJobs } from '../../api/Export/export';
import { ExportResponse, JobStatus } from '../../api/Export/response';
import { CheckCircleTwoTone, CodeOutlined, ExclamationCircleTwoTone, LoadingOutlined } from '@ant-design/icons';
import { sortItemsByKey } from '../../utils/sortutils';
import styled from 'styled-components';

const { Text, Link } = Typography;
const Container = styled.div`
  background-color: #ffffff;
  padding: 1rem;
`;
const StyledButton = styled(Button)`
    height: 35px;
    width: fit-content;
`;

const CDSW_DOMAIN = import.meta.env.VITE_CDSW_DOMAIN;
const PROJECT_OWNER = import.meta.env.VITE_PROJECT_OWNER;
const PROJECT_NAME = import.meta.env.VITE_CDSW_PROJECT;
const JOBS_URL = `https://${CDSW_DOMAIN}/${PROJECT_OWNER}/${PROJECT_NAME}/jobs`;

const jobStatus = (status: JobStatus) => {
    switch (status) {
        case "success":
            return <CheckCircleTwoTone twoToneColor="#52c41a" />;
        case 'ENGINE_FAILED':
        case 'failure':
            return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
        case 'in progress':
            return <LoadingOutlined spin />;
        default:
            return <Tooltip title={`Error during job execution`}><ExclamationCircleTwoTone twoToneColor="red" /></Tooltip>;
    }
};
const columns: TableProps<ExportResponse>['columns'] = [
    {
        key: 'display_name',
        title: 'Source Dataset',
        dataIndex: 'display_name',
        sorter: sortItemsByKey('display_name')
    }, {
        key: 'display_export_name',
        title: 'Export Name',
        dataIndex: 'display_export_name',
        sorter: sortItemsByKey('display_export_name'),
    }, {
        key: 'hf_export_path',
        title: 'Export Location',
        dataIndex: 'hf_export_path',
        sorter: sortItemsByKey('hf_export_path'),
        render: (exportPath) => <Link href={exportPath} target="_blank">{exportPath}</Link>
    }, {
        key: 'timestamp',
        title: 'Create Time',
        dataIndex: 'timestamp',
        sorter: sortItemsByKey('timestamp'),
        render: (timestamp) => <DateTime dateTime={timestamp}></DateTime>
    },
    {
        key: 'job_name',
        title: 'Job Name',
        dataIndex: 'job_id',
        sorter: sortItemsByKey('job_name'),
        render: (jobName) => <Text>{jobName}</Text>
    },
    {
        key: 'job_status',
        title: 'Status',
        dataIndex: 'timestamp',
        sorter: sortItemsByKey('job_status'),
        render: (status: JobStatus) => <Flex justify='center' align='center'>
            {jobStatus(status)}
        </Flex>
    },
];

const ExportsTab: React.FC = () => {
    const { isLoading, isError, data, error } = useGetExportJobs();

    return (
        <Container>
            <Row style={{ marginBottom: 16 }}>
                <Col span={24}>
                    <StyledButton icon={<CodeOutlined />} href={JOBS_URL}>Jobs</StyledButton>
                </Col>
            </Row>
            <Table<ExportResponse>
                rowKey={row => row.id}
                columns={columns}
                loading={isLoading}
                dataSource={data || []}
            />
        </Container>
    );
};

export default ExportsTab;