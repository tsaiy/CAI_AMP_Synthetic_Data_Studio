import get from 'lodash/get';
import isEmpty from 'lodash/isEmpty';
import { Form, FormInstance } from "antd";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useGetEvaluate, useModels } from "./hooks";
import EvaluateDataset from './EvaluateDataset';
import { ModelParameters, ViewType } from './types';
import EvaluatorSuccess from './EvaluatorSuccess';

const BASE_API_URL = import.meta.env.VITE_AMP_URL;

const ReevaluatorPage: React.FC = () => {
  const [form] = Form.useForm<FormInstance>();
  const { evaluate_file_name } = useParams();
  const [viewType, setViewType] = useState<ViewType>(ViewType.REEVALUATE_F0RM);
  const [loading, setLoading] = useState(false); 
  const [ ,setErrorMessage] = useState<string | null>(null);
  const [evaluateResult, setEvaluateResult] = useState(null);
  const {
    evaluate,
    dataset,
    prompt,
    examples,
    isLoading
  } = useGetEvaluate(evaluate_file_name as string);
  console.log('evaluate', evaluate);
  const modelsReq = useModels();
  const modelsMap = get(modelsReq, 'modelsMap', {});
  const model_inference_type = get(evaluate, 'inference_type');
  const models = get(modelsReq, `data.models.${model_inference_type}`, []);

  useEffect(() => {
    if (!isEmpty(evaluate)) {
      const parameters: ModelParameters = get(evaluate, 'model_parameters');
      console.log('parameters', parameters);
      const values = form.getFieldsValue();
      console.log('prompt', prompt);
      form.setFieldsValue({
        ...values,
        display_name: get(evaluate, 'display_name'),
        custom_prompt: prompt,
        top_p: get(parameters, 'top_p'),
        top_k: get(parameters, 'top_k'),
        min_p: get(parameters, 'min_p'),
        max_tokens: get(parameters, 'max_tokens'),
        temperature: get(parameters, 'temperature'),
        model_id: get(evaluate, 'model_id'),
        inference_type: get(evaluate, 'inference_type'),
        model_parameters: parameters
      });
      setTimeout(() => {
        form.setFieldValue('model_parameters', parameters);
      }, 3000)
    }
  }, [evaluate]);

  const evaluateDataset = async (formData: any) => {
    const response = await fetch(`${BASE_API_URL}/synthesis/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });
    return response.json();
  }

  const onSubmit = async () => {
    const values = form.getFieldsValue();
      try {
        await form.validateFields();
      } catch(e) {
        console.error(e);
        return;
      }
      
      const formData = {
        ...values,
        export_type: 'local',
        import_type: 'local',
        import_path: get(dataset, 'generate_file_name'),
        is_demo: dataset.total_count > 25 ? false : true,
        use_case: get(dataset, 'use_case')
      }
      
      try {
        setLoading(true);
        const resp = await evaluateDataset(formData);
        if (!isEmpty(resp.status) && resp.status === 'failed') {
          setErrorMessage(resp.error);
        }
        setLoading(false);
        if (resp.output_path) {
          setEvaluateResult(resp);
          setViewType(ViewType.SUCCESS_VIEW);
        }
      
      } catch (e) {
        console.error(e);
        setLoading(false);
      }
  }

  return (
    <>
      {viewType === ViewType.REEVALUATE_F0RM && 
          <EvaluateDataset 
            form={form} 
            onEvaluate={onSubmit}
            models={models} 
            dataset={evaluate} 
            examples={examples}
            modelsMap={modelsMap}
            viewType={viewType}
            evaluate={evaluate} 
            loading={loading} />}
      {viewType === ViewType.SUCCESS_VIEW && 
        <EvaluatorSuccess 
          dataset={dataset}
          result={evaluateResult}
          demo={get(dataset, 'total_count', 0) <= 25} />}      
    </>
  );    
}

export default ReevaluatorPage;