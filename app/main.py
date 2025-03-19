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
from pydantic import BaseModel
from typing import Dict, List, Optional
import subprocess
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
import time
import math
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
from app.migrations.alembic_manager import AlembicMigrationManager
from app.core.config import responses, caii_check
from app.core.path_manager import PathManager


#****************************************Initialize************************************************

# Initialize services
synthesis_service = SynthesisService()
evaluator_service = EvaluatorService()
export_service = Export_Service()
db_manager = DatabaseManager()


#Initialize path manager
path_manager = PathManager()

# Initialize the migration manager
alembic_manager = AlembicMigrationManager("metadata.db")




project_id = os.getenv("CDSW_PROJECT_ID", "local")
if project_id != "local":

    import cmlapi
    from app.services.synthesis_job import SynthesisJob


    # Initialize required components
    client_cml = cmlapi.default_client()
    project_id = os.getenv("CDSW_PROJECT_ID")
    path_manager = PathManager()  # Make sure this is imported
    db_manager = DatabaseManager()  # Make sure this is imported

    # Get runtime_identifier
    base_job_name = 'Synthetic_data_base_job'
    base_job_id = client_cml.list_jobs(project_id,
                                    search_filter='{"name":"%s"}' % base_job_name).jobs[0].id
    template_job = client_cml.get_job(
        project_id=project_id,
        job_id=base_job_id
    )
    runtime_identifier = template_job.runtime_identifier

    #*************************Initialize JOB******************************
    #Initialize SynthesisJob with required parameters
    synthesis_job = SynthesisJob(
        project_id=project_id,
        client_cml=client_cml,
        path_manager=path_manager,
        db_manager=db_manager,
        runtime_identifier=runtime_identifier
    )


def get_job_status( job_id: str) -> str:
    """
    Get the status of a job run
    
    Args:
        job_id (str): The ID of the job to check
        
    Returns:
        str: The status of the most recent job run
    """
    response = client_cml.list_job_runs(
        project_id, 
        job_id, 
        sort="-created_at", 
        page_size=1
    )
    return response.job_runs[0].status

def get_total_size(file_paths):
  
    file_sizes = []
    for file_path in file_paths:
        
        final_path =  path_manager.get_str_path(file_path)
        file_sizes.append(client_cml.list_project_files(project_id, final_path).files[0].file_size)
        
    total_bytes = sum(int(float(size)) for size in file_sizes) 
    total_gb = math.ceil(total_bytes / (1024 ** 3))

    return total_gb

def restart_application():
    """Restart the CML application"""
    try:
        cml = cmlapi.default_client()
        project_id = os.getenv("CDSW_PROJECT_ID")
        apps_list = cml.list_applications(project_id).applications
        found_app_list = list(filter(lambda app: 'Synthetic Data Studio' in app.name, apps_list))
            
        if len(found_app_list) > 0:
            app = found_app_list[0]
            if app.status == "APPLICATION_RUNNING":
                try:
                    cml.restart_application(project_id, app.id)
                except Exception as e:
                    raise (f"Failed to restart application {app.name}: {str(e)}")
        else:
            raise ValueError("Synthetic Data Studio application not found")
                
    except Exception as e:
        print(f"Error restarting application: {e}")
        raise




# Add these models
class StudioUpgradeStatus(BaseModel):
    git_local_commit: str
    git_remote_commit: str
    updates_available: bool

class StudioUpgradeResponse(BaseModel):
    success: bool
    message: str
    git_updated: bool
    frontend_rebuilt: bool






@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI application"""
    # Create document upload directory on startup
    path_manager.make_dirs(path_manager.upload_dir)
    print(f"Document upload directory created at: {UPLOAD_DIR}")
    yield

app = FastAPI(
    title="LLM Data Synthesis API",
    description="API for generating synthetic question-answer pairs using LLMs",
    version="1.0.0",
    lifespan=lifespan
)



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
    elif path.endswith("/freeform"):
        return 200.0  # 2 minutes for generation
    elif path.endswith("/evaluate"):
        return 200.0  # 2 minutes for evaluation
    elif path.endswith("/export_results"):
        return 200.0  # 2 minutes for export
    elif "health" in path:
        return 5.0    # Quick timeout for health checks
    elif path.endswith("/upgrade"):
        return 1200  # timeout increase for upgrade  
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



@app.on_event("startup")
async def startup_event():
    """Check for and apply any pending migrations on startup"""
    success, message = await alembic_manager.handle_database_upgrade()
    if not success:
        print(f"Warning: {message}")

@app.post("/get_project_files", include_in_schema=True, responses = responses, 
           description = "get project file details")
async def get_project_files(request: RelativePath):
    file_path = path_manager.get_str_path(request.path)
    return client_cml.list_project_files(project_id, file_path)
    
    

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
        caii_endpoint = request.caii_endpoint
        response = caii_check(caii_endpoint)
        message = "The CAII endpoint you are tring to reach is downscaled, please try after >15 minutes while it autoscales, meanwhile please try another model"
        if response.status_code != 200:
                    return JSONResponse(
                        status_code=503,  # Service Unavailable
                        content={"status": "failed", "error": message}
                    )
       
    
    is_demo = request.is_demo
    mem = 4
    core = 2
    if project_id != "local":
        if request.doc_paths:
            paths = request.doc_paths
            data_size = get_total_size(paths)
            if data_size > 1 and data_size <=10:
                is_demo = False
                mem = data_size +2
                core = max(2,data_size//2)
                
            elif data_size >10:
                return JSONResponse(
                        status_code=413,  # Payload Too Large
                        content={
                            "status": "failed",
                            "error": f"Total dataset size ({data_size:} GB) exceeds limit of 10 GB. Please select smaller datasets."
                        }
                    )
            else:
                is_demo = request.is_demo
                mem = 4
                core = 2
  
    
    if is_demo== True:
        if request.input_path:
            return await synthesis_service.generate_result(request,is_demo)
        else:
            return await synthesis_service.generate_examples(request,is_demo)
    else:
       return synthesis_job.generate_job(request, core, mem)
    

@app.post("/synthesis/freeform", include_in_schema=True,
    responses=responses,
    description="Generate freeform structured data")
async def generate_freeform_data(request: SynthesisRequest):
    """Generate freeform structured data based on provided examples and custom instructions"""
    
    if request.inference_type == "CAII":
        caii_endpoint = request.caii_endpoint
        response = caii_check(caii_endpoint)
        message = "The CAII endpoint you are trying to reach is downscaled, please try after >15 minutes while it autoscales, meanwhile please try another model"
        if response.status_code != 200:
            return JSONResponse(
                status_code=503,  # Service Unavailable
                content={"status": "failed", "error": message}
            )
    
    is_demo = request.is_demo
    mem = 4
    core = 2
    if project_id != "local":
        if request.doc_paths:
            paths = request.doc_paths
            data_size = get_total_size(paths)
            if data_size > 1 and data_size <= 10:
                is_demo = False
                mem = data_size + 2
                core = max(2, data_size // 2)
            elif data_size > 10:
                return JSONResponse(
                    status_code=413,  # Payload Too Large
                    content={
                        "status": "failed",
                        "error": f"Total dataset size ({data_size:} GB) exceeds limit of 10 GB. Please select smaller datasets."
                    }
                )
            else:
                is_demo = request.is_demo
                mem = 4
                core = 2
    
    if is_demo:
        return await synthesis_service.generate_freeform(request, is_demo=is_demo)
    else:
        # Pass additional parameter to indicate this is a freeform request
        request_dict = request.model_dump()
        request_dict['generation_type'] = 'freeform'
        # Convert back to SynthesisRequest object
        freeform_request = SynthesisRequest(**request_dict)
        return synthesis_job.generate_job(freeform_request, core, mem)

@app.post("/synthesis/evaluate", 
    include_in_schema=True,
    responses=responses,
    description="Evaluate generated QA pairs")
async def evaluate_examples(request: EvaluationRequest):
    """Evaluate generated QA pairs"""
    if request.inference_type== "CAII":
        caii_endpoint = request.caii_endpoint
        response = caii_check(caii_endpoint)
        message = "The CAII endpoint you are tring to reach is downscaled, please try after >15 minutes while it autoscales, meanwhile please try another model"
        if response.status_code != 200:
                    return JSONResponse(
                        status_code=503,  # Service Unavailable
                        content={"status": "failed", "error": message}
                    )
   
    is_demo = request.is_demo
    if is_demo:
       return evaluator_service.evaluate_results(request)
    
    else:
        return synthesis_job.evaluate_job(request)


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
        return synthesis_job.export_job(request)
    
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
    

def sort_unique_models(model_list):
    def get_sort_key(model_name):
        # Strip any provider prefix
        name = model_name.split('.')[-1] if '.' in model_name else model_name
        parts = name.split('-')
        
        # Extract version
        version = '0'
        for part in parts:
            if part.startswith('v') and any(c.isdigit() for c in part):
                version = part[1:]
                if ':' in version:
                    version = version.split(':')[0]
        
        # Extract date
        date = '00000000'
        for part in parts:
            if len(part) == 8 and part.isdigit():
                date = part
        
        return (float(version), date)
    
    # Remove duplicates while preserving original names
    unique_models = set()
    filtered_models = []
    for model in model_list:
        base_name = model.split('.')[-1] if '.' in model else model
        if base_name not in unique_models:
            unique_models.add(base_name)
            filtered_models.append(model)
    
    return sorted(filtered_models, key=get_sort_key, reverse=True)

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

    

    try:
        client_s = boto3.client(service_name="bedrock", region_name=region, config=retry_config)
        
        # Get foundation models
        response = client_s.list_foundation_models()
        all_models = response['modelSummaries']

        mod_list = [m['modelId']
            for m in all_models 
            if 'ON_DEMAND' in m['inferenceTypesSupported'] 
            and 'TEXT' in m['inputModalities'] 
            and 'TEXT' in m['outputModalities']
            and m['providerName'] in ['Anthropic', 'Meta', 'Mistral AI']]
        
        # Get inference profiles with comprehensive error handling
        try:
            inference_models = client_s.list_inference_profiles()
            inference_mod_list = []
            if 'inferenceProfileSummaries' in inference_models:
                inference_mod_list = [
                    m['inferenceProfileId'] 
                    for m in inference_models['inferenceProfileSummaries']
                    if any(provider in m['inferenceProfileId'].lower() 
                        for provider in ['meta', 'anthropic', 'mistral'])
                ]
        except client_s.exceptions.ResourceNotFoundException:
            inference_mod_list = []
        except client_s.exceptions.ValidationException as e:
            print(f"Validation error: {str(e)}")
            inference_mod_list = []
        except client_s.exceptions.AccessDeniedException as e:
            print(f"Access denied: {str(e)}")
            inference_mod_list = []
        except client_s.exceptions.ThrottlingException as e:
            print(f"Request throttled: {str(e)}")
            inference_mod_list = []
        except client_s.exceptions.InternalServerException as e:
            print(f"Bedrock internal error: {str(e)}")
            inference_mod_list = []
        
        # Combine and sort the lists
        bedrock_list = sort_unique_models(inference_mod_list + mod_list)
        
        models = {
            "aws_bedrock": bedrock_list,
            "CAII": ['meta/llama-3_1-8b-instruct', 'mistralai/mistral-7b-instruct-v0.3']
        }

        return {"models": models}
    
    except client_s.exceptions.ValidationException as e:
        print(f"Validation error: {str(e)}")
        raise
    except client_s.exceptions.AccessDeniedException as e:
        print(f"Access denied: {str(e)}")
        raise
    except client_s.exceptions.ThrottlingException as e:
        print(f"Request throttled: {str(e)}")
        raise
    except client_s.exceptions.InternalServerException as e:
        print(f"Bedrock internal error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        raise

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
            "top_k": {"min": 0, "max": 300, "default": 50},
            "max_tokens": {"min": 1, "max": 8192, "default": 8192}
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

@app.get("/dataset_details/{file_path}", include_in_schema=True)
async def get_dataset(file_path: str):
    with open(file_path) as f:
            data = json.load(f)
    
   
    if 'qa_pairs' and 'evaluated' in file_path:
            for key in data:
                if key != "Overall_Average" and isinstance(data[key], dict):
                    data[key]["evaluated_pairs"] = data[key]["evaluated_pairs"][:100]
            return {"evaluation": data}
            
    elif 'qa_pairs' in file_path:
            return {'generation': data[0:100]}

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


# Add these two endpoints
@app.get("/synthesis-studio/check-upgrade", response_model=StudioUpgradeStatus)
async def check_upgrade_status():
    """Check if any upgrades are available"""
    try:
        with path_manager.in_project_directory():
            # Fetch latest changes
            subprocess.run(["git", "fetch"], check=True, capture_output=True)
            
            # Get current branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                check=True, 
                capture_output=True, 
                text=True
            ).stdout.strip()
            
            # Get local and remote commits
            local_commit = subprocess.run(
                ["git", "rev-parse", branch],
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            remote_commit = subprocess.run(
                ["git", "rev-parse", f"origin/{branch}"],
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            updates_available = local_commit != remote_commit
            
            return StudioUpgradeStatus(
                git_local_commit=local_commit,
                git_remote_commit=remote_commit,
                updates_available=updates_available
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesis-studio/upgrade", response_model=StudioUpgradeResponse)
async def perform_upgrade():
    """
    Perform upgrade process:
    1. Pull latest code
    2. Run database migrations with Alembic
    3. Run build_client.sh
    4. Run start_application.py
    5. Restart CML application
    """
    try:
        messages = []
        git_updated = False
        frontend_rebuilt = False
        db_upgraded = False
        
        # 1. Git operations
        try:
            with path_manager.in_project_directory():
                # Stash any changes
                subprocess.run(["git", "stash"], check=True, capture_output=True)
                
                # Pull updates
                subprocess.run(["git", "pull"], check=True, capture_output=True)
                
                # Try to pop stash
                try:
                    subprocess.run(["git", "stash", "pop"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    messages.append("Warning: Could not restore local changes")
                
                git_updated = True
                messages.append("Git repository updated")
            
        except subprocess.CalledProcessError as e:
            messages.append(f"Git update failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        # 2. Database migrations
        try:
            db_success, db_message = await alembic_manager.handle_database_upgrade()
            if db_success:
                db_upgraded = True
                messages.append(db_message)
            else:
                messages.append(f"Database upgrade failed: {db_message}")
                raise HTTPException(status_code=500, detail=db_message)
        except Exception as e:
            messages.append(f"Database migration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
        # 3. Run build_client.sh
        try:
            # script_path = "build/build_client.py"
            # #script_path = path_manager.get_str_path(script_path)
            # subprocess.run(["python", script_path], check=True)
            subprocess.run(["bash build/shell_scripts/build_client.sh"], shell=True, check=True)
            frontend_rebuilt = True
            messages.append("Frontend rebuilt successfully")
        except subprocess.CalledProcessError as e:
            messages.append(f"Frontend build failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
       
        if git_updated or frontend_rebuilt or db_upgraded:
            try:
                # Small delay to ensure logs are captured
                time.sleep(10)
                restart_application()
                messages.append("Application restart initiated")
                
                # Note: This response might not reach the client due to the restart
                return StudioUpgradeResponse(
                    success=True,
                    message="; ".join(messages),
                    git_updated=git_updated,
                    frontend_rebuilt=frontend_rebuilt
                )
                
            except Exception as e:
                messages.append(f"Application restart failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upgrade failed: {str(e)}"
        )
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