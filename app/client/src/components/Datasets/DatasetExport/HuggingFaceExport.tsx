import { Form, Input } from "antd";
import { HuggingFaceConfiguration } from "../../../api/Datasets/request";
import { useCallback, useEffect } from "react";

const HF_TOKEN = import.meta.env.VITE_HF_TOKEN;
const HF_USERNAME = import.meta.env.VITE_HF_USERNAME;

const INITIAL_EXPORT_CONFIGURATION = {
    hf_repo_name: "",
    hf_username: HF_USERNAME,
    hf_token: HF_TOKEN,
    hf_commit_message: "Default commit message"
}

export type HuggingFaceExportProps = {
    initialExportConfiguration?: HuggingFaceConfiguration;
    setExportConfiguration: (exportConfiguration: HuggingFaceConfiguration) => void;
    isExportConfigValid: (isValid: boolean) => void;
}

export default function HuggingFaceExport({ setExportConfiguration, isExportConfigValid, initialExportConfiguration = INITIAL_EXPORT_CONFIGURATION }: HuggingFaceExportProps) {
    const [form] = Form.useForm<HuggingFaceConfiguration>();
    const formValues = Form.useWatch(() => form.getFieldsValue(), form);
    const isFormValid = useCallback(async () => {
        try {
            await form.validateFields();
            return true;
        } catch {
            return false;
        }
    }, [form]);

    useEffect(() => {
        async function checkFormValidity() {
            const isValid = await isFormValid();
            isExportConfigValid(isValid);
        }

        checkFormValidity();
        setExportConfiguration(formValues);
    }, [formValues, isFormValid, isExportConfigValid, setExportConfiguration]);

    function setInitialExportConfiguration() {
        const initial = { ...initialExportConfiguration, hf_token: HF_TOKEN, hf_username: HF_USERNAME };
        return initial;
    }

    return (
        <>
            <Form
                form={form}
                name="huggingfaceExportConfiguration"
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 14 }}
                initialValues={{ ...setInitialExportConfiguration(), remember: true }}
                autoComplete="on">
                <Form.Item<HuggingFaceConfiguration>
                    label="Repository Name"
                    name="hf_repo_name"
                    tooltip={{ title: "The name of the repository you would like to create" }}
                    rules={[
                        { required: true, message: "Repository Name is required!" },
                        { pattern: /^[a-zA-Z0-9-_]+$/, message: "Repository Name can only include letters, numbers, hyphens, and underscores!" }
                    ]}>
                    <Input />
                </Form.Item>
                <Form.Item<HuggingFaceConfiguration>
                    label="Repository Namespace"
                    name="hf_username"
                    tooltip={{ title: "The namespace you would like to create the repository in" }}
                    rules={[{ required: true, message: "Repository Namespace is required!" }]}>
                    <Input />
                </Form.Item>
                <Form.Item<HuggingFaceConfiguration>
                    label="Access Token"
                    name="hf_token"
                    tooltip={{ title: "Your Huggingface personal access token" }}
                    rules={[{ required: true, message: "Access Token is required!" }]}>
                    <Input />
                </Form.Item>
                <Form.Item<HuggingFaceConfiguration>
                    label="Commit Message"
                    name="hf_commit_message"
                    tooltip={{ title: "The message you would like to use for the commit" }}
                    rules={[{ required: true, message: "Commit Message is required!" }]}>
                    <Input />
                </Form.Item>
            </Form>
        </>
    );
};