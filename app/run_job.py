# run_job.py

import subprocess
import sys
import os
import traceback

if os.getenv("IS_COMPOSABLE"):
    os.chdir("/home/cdsw/synthetic-data-studio")

def check_and_install_requirements():
    """Check and install requirements from requirements.txt"""
    # Get the current working directory instead of using __file__
    current_dir = os.getcwd()
    requirements_path = os.path.join(current_dir, 'requirements.txt')
    
    if os.path.exists(requirements_path):
        try:
            print(f"Installing requirements from: {requirements_path}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            sys.exit(1)
    else:
        print("No requirements.txt found, continuing with existing packages")

# import sys
# venv_path = os.path.join(os.path.dirname(os.path.abspath('')), '.venv/lib/python3.x/site-packages')
# if venv_path not in sys.path:
#     sys.path.insert(0, venv_path)

# Run installation check at start
check_and_install_requirements()

import json
from app.models.request_models import SynthesisRequest
from app.services.synthesis_service import SynthesisService
import asyncio
import nest_asyncio  # Add this import

# Enable nested event loop
nest_asyncio.apply()

async def run_synthesis(request, job_name):
    """Run standard synthesis job for question-answer pairs"""
    try:
        job = SynthesisService()
        if request.input_path:
            result = await job.generate_result(request, job_name, is_demo=False)
        else:
            result = await job.generate_examples(request, job_name, is_demo=False)
        
        return result
    except Exception as e:
        print(f"Error in synthesis: {e}")
        raise

async def run_freeform_synthesis(request, job_name):
    """Run freeform data synthesis job"""
    try:
        job = SynthesisService()
        result = await job.generate_freeform(request, job_name, is_demo=False)
        return result
    except Exception as e:
        print(f"Error in freeform synthesis: {e}")
        raise

if __name__ == "__main__":
    try:
        file_name = os.environ.get('file_name', '')   # Get filename from environment variables

        # Read JSON file
        with open(file_name, 'r') as f:
            params = json.load(f)
        
        job_name = params.pop('job_name')
        print(f"Starting job: {job_name}")
        print(f"Parameters: {params}")
        
        # Clean up the params file after reading
        os.remove(file_name)
        
        # Check if this is a freeform generation request
        is_freeform = params.pop('generation_type', None) == 'freeform'
        
        # Create request object
        request = SynthesisRequest.model_validate(params)
        
        # Get current loop or create new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run appropriate synthesis based on type
        if is_freeform:
            print("Running freeform data generation job")
            result = loop.run_until_complete(run_freeform_synthesis(request, job_name))
        else:
            print("Running standard question-answer generation job")
            result = loop.run_until_complete(run_synthesis(request, job_name))
            
        print(f"Job completed successfully: {result}")
        
    except Exception as e:
        print(f"Error in job execution: {e}")
        traceback.print_exc()
        sys.exit(1)