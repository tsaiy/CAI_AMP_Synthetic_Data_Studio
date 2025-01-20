import { Button, Form, Modal, Select } from "antd";
import { DatasetResponse, ExportDatasetResponse } from "../../../api/Datasets/response";
import { useEffect, useState } from "react";
import { DatasetExportRequest, HuggingFaceConfiguration } from "../../../api/Datasets/request";
import { EXPORT_TYPE_LABELS, ExportType } from "../../../types";
import HuggingFaceExport from "./HuggingFaceExport";
import { usePostExportDataset } from "../../../api/Datasets/datasets";

export type ExportResult = {
    successMessage: ExportDatasetResponse | null;
    failedMessage: Error | null;
}

export type ExportModalProps = {
    datasetDetails: DatasetResponse;
    isModalActive: boolean;
    setIsModalActive: (isActive: boolean) => void;
    setExportResult: (exportResult: ExportResult) => void;
}

export default function DatasetExportModal({ isModalActive, datasetDetails, setIsModalActive, setExportResult }: ExportModalProps) {
    const { data: exportData, loading: exportLoading, error: exportError, triggerPost: triggerExport } = usePostExportDataset();
    const [form] = Form.useForm();
    const [exportConfiguration, setExportConfiguration] = useState<HuggingFaceConfiguration>();
    const [isHugginfaceConfigValid, setIsHugginfaceConfigValid] = useState(false);


    useEffect(() => {
        setExportConfiguration({ hf_repo_name: datasetDetails.display_name, hf_commit_message: "Default commit message" } as HuggingFaceConfiguration);
    }, [datasetDetails]);

    async function handleExport() {
        let exportConfigurationBody = {};
        const selectedExportType = form.getFieldValue("export_type");

        switch (selectedExportType) {
            case "huggingface": {
                exportConfigurationBody = { hf_config: exportConfiguration };
                break;
            }
            default: {
                break;
            }
        }

        const data: DatasetExportRequest = {
            export_type: [selectedExportType],
            file_path: datasetDetails.local_export_path,
            ...exportConfigurationBody
        };

        await triggerExport(data);
        setIsModalActive(false);
    }

    useEffect(() => {
        const exportResult: ExportResult = { successMessage: exportData, failedMessage: exportError };
        setExportResult(exportResult);
    }, [exportData, exportError]);

    function handleClose() {
        form.resetFields()
        setIsModalActive(false);
    }

    const exportTypes = Object.entries(EXPORT_TYPE_LABELS).map(([key]) => <Select.Option key={key} value={key}>{EXPORT_TYPE_LABELS[key as ExportType]}</Select.Option>);

    return (
        <Modal title={`Export Dataset`}
            width={"50%"}
            open={isModalActive}
            destroyOnClose={true}
            onCancel={handleClose}
            onClose={handleClose}
            footer={
                <>
                    <Button type="default" onClick={handleClose}>Cancel</Button>
                    <Button type="primary" loading={exportLoading} disabled={!isHugginfaceConfigValid} onClick={handleExport}>Export</Button>
                </>
            }>
            <Form
                form={form}
                name="exportModal"
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 14 }}
                initialValues={{ export_type: "huggingface" }}
                autoComplete="on"
                preserve={false}
            >
                <Form.Item<ExportType>
                    label="Export Type"
                    name="export_type"
                    tooltip={{ title: "Select the type of export you would like to perform" }}
                    rules={[{ required: true, message: "Export Type is required!" }]}>
                    <Select
                        style={{ width: "100%" }}>
                        {exportTypes}
                    </Select>
                </Form.Item>
            </Form>

            <HuggingFaceExport initialExportConfiguration={exportConfiguration} isExportConfigValid={setIsHugginfaceConfigValid} setExportConfiguration={setExportConfiguration} />

        </Modal>
    )
}