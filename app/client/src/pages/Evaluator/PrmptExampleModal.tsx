import { Flex, Form, Input, Modal } from 'antd';
import styled from 'styled-components';
import TooltipIcon from '../../components/TooltipIcon';
import { EvaluateExample, EvaluateExampleRecord } from './types';
import { MODE } from './util';


const JustificationInput = styled(Input.TextArea)`
    min-height: 150px !important;
    resize: none !important;
`

interface Props {
  mode: MODE;  
  example: EvaluateExampleRecord | null;
  onClose: () => void;
  onSave: (prompt: EvaluateExample, index: number) => void;
}


const PromptExampleModal: React.FC<Props> = ({ example, onClose, onSave }) => {
    const [form] = Form.useForm();

  const onSubmit = async () => {
    form.submit()
    const data = form.getFieldsValue();  
    try {
        await form.validateFields();
    } catch(e) {
        console.error(e);
        return;
    }  
    onSave(data, example?.index as number);
  }
    
    const initialValues = {
      justification: example?.justification,
      score: example?.score       
    };
    
    return (
      <Modal
        visible={true}
        okText={'Save'}
        title={'Edit Prompt Example'}
        onCancel={onClose}
        onOk={onSubmit}
        width="70%"
      >  
      <Form 
        layout="vertical"
        form={form} 
        initialValues={initialValues}
      >
        <Flex gap={15} vertical>
                 <div style={{ marginTop: '8px' }}>
                    <Form.Item
                        name='justification'
                        label={
                          <Flex>
                            <div style={{ marginRight: '4px' }}>Justification</div>
                            <TooltipIcon message={'Provide a justification for the evaluate example.'} size={14}/>
                          </Flex>    
                        }
                        rules={[
                            { required: true, message: 'This field is required.' }
                        ]}
                    >
                        <JustificationInput placeholder={'Enter a justification'}/>
                    </Form.Item>
                </div>
                <div>
                   
                    <Form.Item
                        name='score'
                        label={
                          <Flex>
                            <div style={{ marginRight: '4px' }}>Score</div>
                            <TooltipIcon message={'Provide a numerical score for the evaluate example.'} size={14}/>
                          </Flex>
                        }
                        rules={[
                            { required: true, message: 'This field is required.' }
                        ]}
                    >
                        <Input type="number" min={0} max={5} style={{ width: '150px' }}/>
                    </Form.Item>

                </div>
            </Flex>
        </Form>
      </Modal>  
    )
}

export default PromptExampleModal;