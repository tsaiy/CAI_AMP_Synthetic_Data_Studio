import os
import boto3
from datetime import datetime, timezone
from botocore.config import Config
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from asyncio import TimeoutError, wait_for
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
import time
import requests
from requests.exceptions import ReadTimeout
from urllib3.exceptions import ReadTimeoutError
import sys
import json
import uuid 
print(os.getcwd())
# Setup absolute paths
ROOT_DIR = Path(__file__).parent.parent  # Goes up one level from app/main.py to reach project root
print("root: ", Path(__file__))
APP_DIR = ROOT_DIR / "app"

UPLOAD_DIR = ROOT_DIR / "document_upload" 

# Add the project root to Python path to enable absolute imports
sys.path.append(str(ROOT_DIR))

from app.services.evaluator_service import EvaluatorService
from app.models.request_models import SynthesisRequest, EvaluationRequest, Export_synth, ModelParameters, CustomPromptRequest, JsonDataSize, RelativePath
from app.services.synthesis_service import SynthesisService
from app.services.export_results import Export_Service
from app.core.prompt_templates import PromptBuilder, PromptHandler
from app.core.config import UseCase, USE_CASE_CONFIGS
from app.core.database import DatabaseManager
from app.core.exceptions import APIError, InvalidModelError, ModelHandlerError
from app.services.model_alignment import ModelAlignment
from app.core.model_handlers import create_handler
from app.services.aws_bedrock import get_bedrock_client

#*************Comment this when running locally********************************************
import cmlapi
client_cml = cmlapi.default_client()
project_id = os.getenv("CDSW_PROJECT_ID")
base_job_name = 'Synthetic_data_base_job'
base_job_id = client_cml.list_jobs(project_id,
                                   search_filter='{"name":"%s"}' % base_job_name).jobs[0].id
template_job = client_cml.get_job(
    project_id=project_id,
    job_id=base_job_id
)
runtime_identifier = template_job.runtime_identifier

def get_job_status(job_id):
    response = client_cml.list_job_runs(project_id, job_id, sort="-created_at", page_size=1)
    return response.job_runs[0].status

#*************Comment this when running locally********************************************

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI application"""
    # Create document upload directory on startup
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"Document upload directory created at: {UPLOAD_DIR}")
    yield



app = FastAPI(
    title="LLM Data Synthesis API",
    description="API for generating synthetic question-answer pairs using LLMs",
    version="1.0.0",
    lifespan=lifespan
)

responses = {
    # 4XX Client Errors
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request - Invalid input parameters",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Invalid input: No topics provided"
                }
            }
        }
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Requested resource not found"
                }
            }
        }
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Invalid request parameters"
                }
            }
        }
    },

    # 5XX Server Errors
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Internal server error occurred"
                }
            }
        }
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Service temporarily unavailable",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "The CAII endpoint is downscaled, please try after >15 minutes"
                }
            }
        }
    },
    status.HTTP_504_GATEWAY_TIMEOUT: {
        "description": "Request timed out",
        "content": {
            "application/json": {
                "example": {
                    "status": "failed",
                    "error": "Operation timed out after specified seconds"
                }
            }
        }
    }
}



@app.middleware("http")
async def global_middleware(request: Request, call_next):
    try:
        timeout_seconds = get_timeout_for_request(request)
        response = await wait_for(
            call_next(request),
            timeout=timeout_seconds
        )
        return response
        
    except TimeoutError:
        endpoint_name = request.url.path.split('/')[-1]
        return JSONResponse(
            status_code=504,
            content={
                "status": "failed", 
                "error": f"Operation '{endpoint_name}' timed out after {timeout_seconds} seconds"
            }
        )
    except APIError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"status": "failed", "error": e.message}
        )
    except RuntimeError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "failed", "error": str(e)}
        )
    
    except InvalidModelError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"status": "failed", "error": e.message}
        )
    
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "error": str(e)}
        )
    
def get_timeout_for_request(request: Request) -> float:
    """
    Get timeout duration based on endpoint
    """
    path = request.url.path
    
    # Longer timeouts for job creation endpoints
    if path.endswith("/generate"):
        return 200.0  # 2 minutes for generation
    elif path.endswith("/evaluate"):
        return 200.0  # 2 minutes for evaluation
    elif path.endswith("/export_results"):
        return 200.0  # 2 minutes for export
    elif "health" in path:
        return 5.0    # Quick timeout for health checks
    else:
        return 60.0   # Default timeout


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
synthesis_service = SynthesisService()
evaluator_service = EvaluatorService()
export_service = Export_Service()
db_manager = DatabaseManager()



@app.post("/get_project_files", include_in_schema=True, responses = responses, 
           description = "get project file details")
async def get_project_files(request:RelativePath):
    if os.getenv("IS_COMPOSABLE"):
        root_path = "synthetic-data-studio"
    else:
        root_path = ""
    final_path = os.path.join(root_path, request.path)

    return client_cml.list_project_files(project_id, final_path)
    
    

@app.post("/json/dataset_size", include_in_schema=True, responses = responses,
          description = "get total dataset size for jsons")
async def get_dataset_size(request:JsonDataSize):

    if request.input_path:
        inputs = []
        file_paths = request.input_path
        for path in file_paths:
            try:
                with open(path) as f:
                    data = json.load(f)
                    if not data:
                        raise ValueError(f"Empty JSON data in file: {path}")
                    
                    # Check if input_key exists in at least one item
                    key_exists = any(request.input_key in item for item in data)
                    if not key_exists:
                        raise KeyError(f"Input key '{request.input_key}' not found in any item in file: {path}")
                    
                    # Collect values, raising error if any item is missing the key
                    for item in data:
                        if request.input_key not in item:
                            raise KeyError(f"Input key '{request.input_key}' missing in item: {item}")
                        inputs.append(item[request.input_key])
                        
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format in file {path}: {str(e)}"
                print(error_msg)
                return JSONResponse(
                    status_code=400,
                    content={"status": "failed", "error": error_msg}
                )
            except (KeyError, ValueError) as e:
                print(str(e))
                return JSONResponse(
                    status_code=400,
                    content={"status": "failed", "error": str(e)}
                )
            except Exception as e:
                error_msg = f"Error processing {path}: {str(e)}"
                print(error_msg)
                return JSONResponse(
                    status_code=400,
                    content={"status": "failed", "error": error_msg}
                )
            
    return {"dataset_size": len(inputs)}


@app.post("/synthesis/generate", include_in_schema=True,
    responses=responses,
    description="Generate question-answer pairs")
async def generate_examples(request: SynthesisRequest):
    """Generate question-answer pairs"""
    
    if request.inference_type== "CAII":
        print("I am here")
        API_KEY = json.load(open("/tmp/jwt"))["access_token"]
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        message = "The CAII endpoint you are tring to reach is downscaled, please try after >15 minutes while it autoscales, meanwhile please try another model"
        caii_endpoint = request.caii_endpoint
        if caii_endpoint:
            caii_endpoint = caii_endpoint.removesuffix('/chat/completions') 
            caii_endpoint = caii_endpoint + "/health/ready"
            response = requests.get(caii_endpoint, headers=headers, timeout=3)  # Will raise RequestException if fails

            try:
                    response = requests.get(caii_endpoint, headers = headers, timeout=3)
                    if response.status_code != 200:
                        return JSONResponse(
                            status_code=503,  # Service Unavailable
                            content={"status": "failed", "error": message}
                        )
            except:
                return JSONResponse(
                        status_code=503,  # Service Unavailable
                        content={"status": "failed", "error": message}
                    )

    
  
    is_demo = request.is_demo
    

    if is_demo== True:
        if request.input_path:
            return await synthesis_service.generate_result(request,is_demo)
        else:
            return await synthesis_service.generate_examples(request,is_demo)
   
        
    else:
        # Convert to JSON for job arguments
        json_str = request.model_dump_json()  # This gives us a JSON string directly
        #compact_json = json_str.replace(" ", "")
        if os.getenv("IS_COMPOSABLE"):
            script_path = "synthetic-data-studio/app/run_job.py"
        else:
            script_path = "app/run_job.py"
        
        
        random_id = uuid.uuid4().hex[:4]  # Generate a random 8-character ID
        
        if request.display_name:
            job_name = f"{request.display_name}_{random_id}"
        else:
            job_name = f"synth_job_{random_id}"
        

        params = json.loads(json_str)
        params['job_name'] = job_name  # Add job_name to the parameters

        # Create unique filename with UUID
        file_name = f"job_args_{random_id}.json"
        
        # Write to local file
        with open(file_name, 'w') as f:
            json.dump(params, f)

        
        job_instance = cmlapi.CreateJobRequest(
            project_id=project_id,
            name=job_name,
            script=script_path,
            runtime_identifier=runtime_identifier,
            cpu=2,
            memory=4,
            environment = {'file_name':file_name}
        )

        created_job = client_cml.create_job(project_id=project_id,
                body=job_instance,
        )
        job_run = client_cml.create_job_run(cmlapi.CreateJobRunRequest(), project_id=project_id, job_id=created_job.id)

        if request.input_path:
            file_path = request.input_path
            with open(file_path, 'r') as file:
                    inputs = json.load(file)
            total_count = len(inputs)
            
            topics = []
            num_questions = None
        else:
            total_count = request.num_questions*len(request.topics)
            
            topics = request.topics
            num_questions = request.num_questions
        examples_str = PromptHandler.get_default_example(request.use_case,request.examples)
        custom_prompt_str = PromptHandler.get_default_custom_prompt(request.use_case, request.custom_prompt)  
       
        schema_str = PromptHandler.get_default_schema(request.use_case, request.schema)
        
        model_params = request.model_params or ModelParameters()
        print(job_run.job_id, job_name)

        if request.doc_paths:
            topic_str = []
        else:
            topic_str = topics
        
        metadata = {
                'technique': request.technique,
                'model_id': request.model_id,
                'inference_type': request.inference_type,
                'use_case': request.use_case,
                'final_prompt': custom_prompt_str,
                'model_parameters': model_params.model_dump(),
                'display_name': request.display_name,
                'num_questions':num_questions,
                'topics': topic_str,
                'examples': examples_str,
                "total_count":total_count,
                'schema': schema_str,
                'doc_paths': request.doc_paths,
                'input_path': request.input_path,
                'job_name':job_name,
                'job_id': job_run.job_id,
                'job_status': get_job_status(job_run.job_id),
                 'output_key':request.output_key,
                'output_value':request.output_value,
               'job_creator_name' : client_cml.list_job_runs(project_id, job_run.job_id,sort="-created_at", page_size=1).job_runs[0].creator.name
                }
        
        db_manager.save_generation_metadata(metadata)

        return {"job_name": job_name, "job_id": job_run.job_id}


@app.post("/synthesis/evaluate", 
    include_in_schema=True,
    responses=responses,
    description="Evaluate generated QA pairs")
async def evaluate_examples(request: EvaluationRequest):
    """Evaluate generated QA pairs"""


    
    if request.inference_type== "CAII":
        print("I am here")
        API_KEY = json.load(open("/tmp/jwt"))["access_token"]
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        caii_endpoint = request.caii_endpoint
        message = "The CAII endpoint you are tring to reach is downscaled, please try after >15 minutes while it autoscales, meanwhile please try another model"
        if caii_endpoint:
             
            caii_endpoint = caii_endpoint.removesuffix('/chat/completions') 
            caii_endpoint = caii_endpoint + "/health/ready"
            try:
                    response = requests.get(caii_endpoint, headers = headers, timeout=3)
                    if response.status_code != 200:
                        return JSONResponse(
                            status_code=503,  # Service Unavailable
                            content={"status": "failed", "error": message}
                        )
            except:
                return JSONResponse(
                        status_code=503,  # Service Unavailable
                        content={"status": "failed", "error": message}
                    )
                
    is_demo = request.is_demo
    if is_demo:
       return evaluator_service.evaluate_results(request)
    
    else:

        json_str = request.model_dump_json()  # This gives us a JSON string directly
        #compact_json = json_str.replace(" ", "")
        
        
        if os.getenv("IS_COMPOSABLE"):
            script_path = "synthetic-data-studio/app/run_eval_job.py"
        else:
            script_path = "app/run_eval_job.py"
        
        
        random_id = uuid.uuid4().hex[:4]  # Generate a random 8-character ID
        
        if request.display_name:
            job_name = f"{request.display_name}_{random_id}"
        else:
            job_name = f"eval_job_{random_id}"
        

        params = json.loads(json_str)
        params['job_name'] = job_name  # Add job_name to the parameters

        # Create unique filename with UUID
        file_name = f"eval_job_args_{random_id}.json"
        
        # Write to local file
        with open(file_name, 'w') as f:
            json.dump(params, f)

        job_instance = cmlapi.CreateJobRequest(
            project_id=project_id,
            name=job_name,
            script=script_path,
            runtime_identifier=runtime_identifier,
            cpu=2,
            memory=4,
            environment = {'file_name':file_name}
        )

        created_job = client_cml.create_job(project_id=project_id,
                body=job_instance,
        )
        job_run = client_cml.create_job_run(cmlapi.CreateJobRunRequest(), project_id=project_id, job_id=created_job.id)

        custom_prompt_str = PromptHandler.get_default_custom_eval_prompt(
                request.use_case, 
                request.custom_prompt
            )
        examples_str = PromptHandler.get_default_eval_example(
            request.use_case,
            request.examples
        )
        model_params = request.model_params or ModelParameters()
        
        metadata = {
            'model_id': request.model_id,
            'inference_type': request.inference_type,
            'use_case': request.use_case,
            'custom_prompt': custom_prompt_str,
            'model_parameters': model_params.model_dump(),
            'generate_file_name': os.path.basename(request.import_path),
            'display_name': request.display_name,
            'examples': examples_str,
            'job_name':job_name,
            'job_id': job_run.job_id,
            'job_status': get_job_status(job_run.job_id),
             'job_creator_name' : client_cml.list_job_runs(project_id, job_run.job_id,sort="-created_at", page_size=1).job_runs[0].creator.name
            
        }

        db_manager.save_evaluation_metadata(metadata)
        

        return {"job_name": job_name, "job_id": job_run.job_id}


@app.post("/model/alignment",
          include_in_schema=True,
          responses=responses,
          description="Generate model alignment data in DPO and KTO formats")
async def generate_alignment_data(
    synthesis_request: SynthesisRequest,
    evaluation_request: EvaluationRequest,
    job_name: str = None,
    is_demo: bool = True
) -> Dict:
    """
    Generate model alignment data using synthesis and evaluation services.
    
    Args:
        synthesis_request: Parameters for synthesis generation
        evaluation_request: Parameters for evaluation
        job_name: Optional job identifier for tracking
        is_demo: Whether this is a demo run
        
    Returns:
        Dictionary containing DPO and KTO formatted data
    """
    try:
        alignment_service = ModelAlignment()
        result = await alignment_service.model_alignment(
            synthesis_request=synthesis_request,
            evaluation_request=evaluation_request,
            job_name=job_name,
            is_demo=is_demo
        )

        
        return {
            "status": "success",
            "dpo": result["dpo"],
            "kto": result["kto"]
        }
        
    except APIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.post("/export_results", include_in_schema=True)
async def export_results(request:Export_synth):
    try: 
        params = request.model_dump()   
       
    
        if os.getenv("IS_COMPOSABLE"):
            script_path = "synthetic-data-studio/app/run_export_job.py"
        else:
            script_path = "app/run_export_job.py"
        
       
        random_id = uuid.uuid4().hex[:4]  # Generate a random 8-character ID


        
        job_name = f"hf_{request.hf_config.hf_repo_name}_{random_id}"
        # Create unique filename with UUID
        file_name = f"hf_export_args_{random_id}.json"
        
        # Write to local file
        with open(file_name, 'w') as f:
            json.dump(params, f)   

    

        

        job_instance = cmlapi.CreateJobRequest(
                project_id=project_id,
                name=job_name,
                script=script_path,
                runtime_identifier=runtime_identifier,
                cpu=2,
                memory=4,
                environment = {'file_name':file_name}
            )

        created_job = client_cml.create_job(project_id=project_id,
                body=job_instance,
        )
        job_run = client_cml.create_job_run(cmlapi.CreateJobRunRequest(), project_id=project_id, job_id=created_job.id)
        repo_id = f"{request.hf_config.hf_username}/{request.hf_config.hf_repo_name}"
        export_path = f"https://huggingface.co/datasets/{repo_id}"

        job_status = get_job_status(job_run.job_id)

        metadata = {"timestamp": datetime.now(timezone.utc).isoformat(),
                    "display_export_name": request.hf_config.hf_repo_name, 
                    "display_name": request.display_name,
                    "local_export_path":request.file_path,
                    "hf_export_path": export_path,
                    "job_id":job_run.job_id,
                    "job_name": job_name,
                    "job_status": job_status,
                     "job_creator_name" : client_cml.list_job_runs(project_id, job_run.job_id,sort="-created_at", page_size=1).job_runs[0].creator.name
                   }
        
        db_manager.save_export_metadata(metadata)

        return  {"job_name": job_name, "job_id": job_run.job_id, "hf_link":export_path}   
    
    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={"status": "failed", "error": f"Unexpected error: {str(e)}"}
        )

@app.post("/create_custom_prompt")
async def create_custom_prompt(request: CustomPromptRequest):
    """Allow users to customize prompt. Only part of the prompt which can be customized"""
    try:
        bedrock_client =   get_bedrock_client()
        model_params = ModelParameters()
        model_handler = create_handler(request.model_id, bedrock_client, model_params, inference_type = request.inference_type, caii_endpoint =  request.caii_endpoint, custom_p = True)
        prompt = PromptBuilder.build_custom_prompt(
                model_id=request.model_id,
                custom_prompt=request.custom_prompt,
            )
        #print(prompt)
        prompt_gen = model_handler.generate_response(prompt)

        return {"generated_prompt":prompt_gen}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/model_ID", include_in_schema=True)
async def get_model_id():
    region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    new_target_region = "us-west-2"
    retry_config = Config(
        region_name=new_target_region,
        retries={
            "max_attempts": 2,
            "mode": "standard",
        },
    ) 
    client_s = boto3.client(service_name="bedrock", region_name=region, config=retry_config)
    response = client_s.list_foundation_models()
    all_models = response['modelSummaries']

    mod_list = [m['modelId']
          for m in all_models 
          if 'ON_DEMAND' in m['inferenceTypesSupported'] 
          and 'TEXT' in m['inputModalities']]
    
    mod_list_wp = {}
    for m in all_models:
        if ('ON_DEMAND' in m['inferenceTypesSupported'] 
                and 'TEXT' in m['inputModalities'] and 'TEXT' in m['outputModalities']):
            provider = m['providerName']
            if provider not in mod_list_wp:
                mod_list_wp[provider] = []
            mod_list_wp[provider].append(m['modelId'])

    models = {"aws_bedrock": ['us.anthropic.claude-3-5-haiku-20241022-v1:0', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                              'us.anthropic.claude-3-opus-20240229-v1:0','anthropic.claude-instant-v1', 
                              'us.meta.llama3-2-11b-instruct-v1:0','us.meta.llama3-2-90b-instruct-v1:0', 'us.meta.llama3-1-70b-instruct-v1:0', 
                                'mistral.mixtral-8x7b-instruct-v0:1', 'mistral.mistral-large-2402-v1:0',
                                   'mistral.mistral-small-2402-v1:0'  ],
             "CAII": ['meta/llama-3_1-8b-instruct', 'mistralai/mistral-7b-instruct-v0.3']
             }

    return {"models":models}

@app.get("/use-cases", include_in_schema=True)
async def get_use_cases():
    """Get available use cases"""
    return {
        "usecases": [
            {"id": UseCase.CODE_GENERATION, "name": "Code Generation"},
            {"id": UseCase.TEXT2SQL, "name": "Text to SQL"},
            {"id": UseCase.CUSTOM, "name": "Custom"}
        ]
    }

@app.get("/model/parameters", include_in_schema=True)
async def get_model_parameters() -> Dict:
   

    return {
        "parameters": {
            "temperature": {"min": 0.0, "max": 2.0, "default": 0.0},
            "top_p": {"min": 0.0, "max": 1.0, "default": 1.0},
            #"min_p": {"min": 0.0, "max": 1.0, "default": 0.0},
            "top_k": {"min": 0, "max": 100, "default": 50},
            "max_tokens": {"min": 1, "max": 8192, "default": 4096}
        }
    }




@app.get("/{use_case}/gen_prompt")
async def customise_prompt(use_case: UseCase):
    """Allow users to customize prompt. Only part of the prompt which can be customized"""
    try:
        return PromptHandler.get_default_custom_prompt(use_case,custom_prompt=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{use_case}/eval_prompt")
async def customise_prompt(use_case: UseCase):
    """Allow users to customize prompt. Only part of the prompt which can be customized"""
    try:
        return PromptHandler.get_default_custom_eval_prompt(use_case, custom_prompt=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sql_schema")
async def customise_prompt():
    """Allow users to customize prompt. Only part of the prompt which can be customized"""
    try:
        use_case = "text2sql"
        return PromptHandler.get_default_schema(use_case,schema=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
@app.get("/generations/history", include_in_schema=True)
async def get_generation_history():
    """Get history of all generations"""
    pending_job_ids = db_manager.get_pending_generate_job_ids()

    if not pending_job_ids:
        return db_manager.get_all_generate_metadata()

    job_status_map = {
            job_id: get_job_status(job_id) 
            for job_id in pending_job_ids
        }
    db_manager.update_job_statuses_generate(job_status_map)
    
    return db_manager.get_all_generate_metadata()

@app.get("/generations/{file_name}", include_in_schema=True)
async def get_generation_by_filename(file_name: str):
    """Get generation metadata by filename"""
    result = db_manager.get_metadata_by_filename(file_name)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No generation found with filename: {file_name}"
        )
    
    return result

@app.get("/exports/history", include_in_schema =True)
def get_exports_history():
    pending_job_ids = db_manager.get_pending_export_job_ids()

    if not pending_job_ids:
        return db_manager.get_all_export_metadata()

    job_status_map = {
            job_id: get_job_status(job_id) 
            for job_id in pending_job_ids
        }
    db_manager.update_job_statuses_export(job_status_map)
    
    return db_manager.get_all_export_metadata()
    

@app.get("/evaluations/history", include_in_schema=True)
async def get_evaluation_history():
    """Get history of all generations"""
    pending_job_ids = db_manager.get_pending_evaluate_job_ids()

    if not pending_job_ids:
        return db_manager.get_all_evaluate_metadata()

    job_status_map = {
            job_id: get_job_status(job_id) 
            for job_id in pending_job_ids
        }
    db_manager.update_job_statuses_evaluate(job_status_map)
    
    
    return db_manager.get_all_evaluate_metadata()


@app.get("/evaluations/{file_name}", include_in_schema=True)
async def get_evaluation_by_filename(file_name: str):
    """Get generation metadata by filename"""
    result = db_manager.get_evaldata_by_filename(file_name)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No evaluation found with filename: {file_name}"
        )
    
    return result



@app.put("/generations/display-name")
async def update_display_name_generate(file_name: str, display_name: str):
    """Update display name for a generation"""
    db_manager.update_generate_display_name(file_name, display_name)
    return {"message": "Display name updated successfully"}

@app.put("/evaluations/display-name")
async def update_display_name_evaluate(file_name: str, display_name: str):
    """Update display name for a generation"""
    db_manager.update_evaluate_display_name(file_name, display_name)
    return {"message": "Display name updated successfully"}

@app.delete("/generations/{file_name}")
async def delete_generation(file_name: str, file_path: Optional[str] = None):
    """Delete generation metadata and optionally delete the local file"""
    db_manager.delete_generate_data(file_name, file_path)
    return {"message": f"Generation data for '{file_name}' has been deleted successfully."}


@app.delete("/evaluations/{file_name}")
async def delete_evaluation(file_name: str, file_path: Optional[str] = None):
    """Delete evaluation metadata and optionally delete the local file"""
    db_manager.delete_evaluate_data(file_name, file_path)
    return {"message": f"Evaluation data for '{file_name}' has been deleted successfully."}





@app.get("/use-cases/{use_case}/topics")
async def get_topics(use_case: UseCase):
    """Get available topics for a specific use case"""
    uc_topics = {"code_generation": ["Algorithms", "Async Programming", 
                                     "Data Structures", "Database Operations", 
                                     "Python Basics", "Web Development"],

        "text2sql":["Aggregations", "Basic Queries", "Data Manipulation", 
                    "Joins", "Subqueries", "Window Functions"],
        "custom": []
    }
    
    topics = uc_topics[use_case]

    return {"topics":topics}

@app.get("/{use_case}/gen_examples")
async def get_gen_examples(use_case: UseCase):
        if use_case ==UseCase.CUSTOM:
            return {"examples":[]}
        else:
            return {"examples": USE_CASE_CONFIGS[use_case].default_examples}

@app.get("/{use_case}/eval_examples")
async def get_eval_examples(use_case: UseCase):
    if use_case == UseCase.CODE_GENERATION:
        examples = [
                    {
        "score": 3,
        "justification": """The code achieves 3 points by implementing core functionality correctly (1), 
        showing generally correct implementation with proper syntax (2), 
        and being suitable for professional use with good Python patterns and accurate functionality (3). 
        While it demonstrates competent development practices, it lacks the robust error handling 
        and type hints needed for point 4, and could benefit from better efficiency optimization and code organization."""
    },
    {
        "score": 4,
        "justification": """
        The code earns 4 points by implementing basic functionality (1), showing correct implementation (2), 
        being production-ready (3), and demonstrating high efficiency with Python best practices 
        including proper error handling, type hints, and clear documentation (4). 
        It exhibits experienced developer qualities with well-structured code and maintainable design, though 
        it lacks the comprehensive testing and security considerations needed for a perfect score."""
    }
            ]
    elif use_case == UseCase.TEXT2SQL:

        examples = [ {
                    "score": 3,
                    "justification": """The query earns 3 points by successfully retrieving basic data (1), 
                    showing correct logical implementation (2), and being suitable for
                    professional use with accurate data retrieval and good SQL pattern understanding (3). 
                    However, it lacks efficiency optimizations and consistent style conventions needed for
                    point 4, using basic JOINs without considering indexing or performance implications. 
                    While functional, the query would benefit from better organization and efficiency improvements."""
                            },

                    {
                "score": 4,
                "justification": """The query merits 4 points by retrieving basic data correctly (1), implementing proper 
                logic (2), being production-ready (3), and demonstrating high efficiency with proper
                indexing considerations, well-structured JOINs, and consistent formatting (4). It 
                shows experienced developer qualities with appropriate commenting and performant SQL 
                features, though it lacks the comprehensive NULL handling and execution plan optimization needed for a 
                perfect score."""
                    }
                    ]
    elif use_case ==UseCase.CUSTOM:
        examples = []
    
    
    return {"examples": examples}

@app.get("/{use_case}/custom_gen_examples")
async def get_custom_gen_examples(use_case: UseCase):
    
                
    if use_case == UseCase.CODE_GENERATION:
        examples = [
        """#Here's how to create and modify a list in Python:
        # Create an empty list\n
        my_list = []
        #  Add elements using append\n
        my_list.append(1)\n
        my_list.append(2)\n\n
        # # Create a list with initial elements
        my_list = [1, 2, 3]
        """,

        """#Here's how to implement a basic stack:class Stack:
        def __init__(self):
        self.items = []
        def push(self, item):
        self.items.append(item)
        def pop(self):
        if not self.is_empty():
        return self.items.pop()
        def is_empty(self):
        return len(self.items) == 0"""
    ]
        
        
    
    elif use_case == UseCase.TEXT2SQL:

        examples = [ """
                    SELECT e.name, d.department_name
                    FROM employees e
                    JOIN departments d ON 
                    e.department_id = d.id;""",

                    """SELECT *
                        FROM employees
                        WHERE salary > 50000;"""
        ]
        
        
    elif use_case == UseCase.CUSTOM:
        examples = []
        
                   
        
    return {"examples": examples}

@app.get("/health")
async def health_check():
    """Get API health status"""
    #return {"status": "healthy"}
    return synthesis_service.get_health_check()

@app.get("/{use_case}/example_payloads")
async def get_example_payloads(use_case:UseCase):
    """Get example payloads for different use cases"""
    if use_case == UseCase.CODE_GENERATION:
        payload = {
                    "use_case": "code_generation",
                    "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                    "num_questions": 3,
                    "technique": "sft",
                    "topics": ["python_basics", "data_structures"],
                    "is_demo": True,
                    "examples":  [
                {
                    "question": "How do you create a list in Python and add elements to it?",
                    "solution": "Here's how to create and modify a list in Python:\n\n```python\n# Create an empty list\nmy_list = []\n\n# Add elements using append\nmy_list.append(1)\nmy_list.append(2)\n\n# Create a list with initial elements\nmy_list = [1, 2, 3]\n```"
                },
                {
                    "question": "How do you implement a stack using a list in Python?",
                    "solution": "Here's how to implement a basic stack:\n\n```python\nclass Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        self.items.append(item)\n    \n    def pop(self):\n        if not self.is_empty():\n            return self.items.pop()\n    \n    def is_empty(self):\n        return len(self.items) == 0\n```"
                }
                ],
                    
                    "model_params": {
                        "temperature": 0.0,  # More precise responses
                        "top_p": 1.0,
                        "top_k": 250,
                        "max_tokens": 4096  # Updated for Claude-3
                    }
                }
    elif use_case == UseCase.TEXT2SQL:
        payload = {
                    "use_case": "text2sql",
                    "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
                    "num_questions": 3,
                    "technique": "sft",
                    "topics": ["basic_queries", "joins"],
                    "is_demo": True,
                    "schema": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255));\nCREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2), FOREIGN KEY (user_id) REFERENCES users(id));",
                    "examples":[
                                {
                                    "question": "How do you select all employees from the employees table?",
                                    "solution": "Here's the SQL query:\n```sql\nSELECT *\nFROM employees;\n```"
                                },
                                {
                                    "question": "How do you join employees and departments tables to get employee names with their department names?",
                                    "solution": "Here's the SQL query:\n```sql\nSELECT e.name, d.department_name\nFROM employees e\nJOIN departments d ON e.department_id = d.id;\n```"
                                }
                            ],
                   
                    "model_params": {
                        "temperature": 0.0,  # More precise responses
                        "top_p": 1.0,
                        "top_k": 250,
                        "max_tokens": 4096  # Updated for Claude-3
                    }
                }
    elif use_case == UseCase.CUSTOM:
        payload = {
            "use_case": "custom",
            "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
            "num_questions": 3,
            "technique": "sft",
            "topics": ["topic 1", "topic 2"],
            "custom_prompt": "Give your instructions here",
            "is_demo": True,
            
            "examples":[
                        {
                            "question": "question 1",
                            "solution": "solution 1"
                        },
                        {
                            "question": "question 2",
                            "solution": "solution 2"
                        }
                    ],
            "export_type": ["local", "huggingface"],
            "model_params": {
                "temperature": 0.0,  
                "top_p": 1.0,
                "top_k": 250,
                "max_tokens": 4096  
            }
        }

    return payload

#****** comment below for testing just backend**************
current_directory = os.path.dirname(os.path.abspath(__file__))
client_build_path = os.path.join(current_directory, "client", "dist")
app.mount("/static", StaticFiles(directory=client_build_path, html=True), name="webapp")

@app.get("/")
async def serve_index():
   return FileResponse(os.path.join(client_build_path, "index.html"))

@app.get("/{path_name:path}")
async def serve_react_app(path_name: str):
   file_path = os.path.join(client_build_path, path_name)

   if os.path.exists(file_path) and os.path.isfile(file_path):
       return FileResponse(file_path)

   return FileResponse(os.path.join(client_build_path, "index.html")) 