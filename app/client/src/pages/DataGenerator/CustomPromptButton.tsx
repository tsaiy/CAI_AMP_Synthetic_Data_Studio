import { Button, Flex, Form, Input, Modal, notification, Spin } from "antd";
import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import styled from "styled-components";
import { LoadingOutlined } from '@ant-design/icons';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { fetchCustomPrompt, fetchPrompt } from "./hooks";
import Loading from "../Evaluator/Loading";

interface Props {
    model_id: string;
    use_case: string;
    inference_type: string;
    caii_endpoint: string;
    setPrompt: (prompt: string) => void
}

export const StyledTextArea = styled(Input.TextArea)`
    margin-bottom: 10px !important;
    min-height: 175px !important;
`;

const CustomPromptButton: React.FC<Props> = ({ model_id, inference_type, caii_endpoint, use_case, setPrompt }) => {
  const [form] = Form.useForm();
  const [showModal, setShowModal] = useState(false);

  const mutation = useMutation({
    mutationFn: fetchCustomPrompt
  });

  useEffect(() => {
      if (mutation.isError) {
          notification.error({
            message: 'Error',
            description: `An error occurred while fetching the prompt.\n ${mutation.error}`
          });
      }
      if (mutation.isSuccess) {
        setPrompt(mutation.data as string);
        setShowModal(false);
      }
  }, [mutation.error, mutation.isSuccess]);

  const onFinish = async () => {
    const custom_prompt = form.getFieldValue('custom_prompt_instructions');
    try { 

      mutation.mutate({
        model_id,
        inference_type,
        caii_endpoint,
        custom_prompt,
        use_case
      })
    } catch(e) {
      console.error(e);
    }

  }
  const onSubmit = () => {}

  const initialValues = {
    custom_prompt_instructions: null
  }

  return (
    <>
      <Button
        onClick={() => setShowModal(true)}
        style={{ marginLeft: '8px' }}
        icon={<AutoAwesomeIcon />}
      />
      {showModal && 
        (
            <Modal
              visible={showModal}
              okText={`Generate`}
              title={`Generate Cutom Prompt`}
              onCancel={() => setShowModal(false)}
              onOk={() => onFinish()}
            >
                <Form 
                    form={form} 
                    layout="vertical" 
                    initialValues={initialValues} 
                    onFinish={onSubmit}
                    style={{ marginTop: '24px' }}
                    disabled={mutation.isLoading}
                >
                    {mutation.isLoading && 
                      <Loading />
                    }

                    <Form.Item
                        name='custom_prompt_instructions'
                        label='Custom Prompt Instructions'
                        rules={[{ required: true, message: "This field is required." }]}
                    >
                        <StyledTextArea 
                            autoSize 
                            placeholder={'Enter instructions for a custom prompt'}
                        />
                    </Form.Item>
                </Form>

            </Modal>
        )
      }
    </>
  );    
}

export default CustomPromptButton;