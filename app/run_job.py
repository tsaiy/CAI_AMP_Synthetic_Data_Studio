# run_job.py

import subprocess
import sys
import os

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

# Run installation check at start
check_and_install_requirements()



import sys
import json
from app.models.request_models import SynthesisRequest, ModelParameters

from app.services.synthesis_service import SynthesisService
import asyncio
import nest_asyncio  # Add this import

# Enable nested event loop
nest_asyncio.apply()

async def run_synthesis(request, job_name):
    try:
        
        job = SynthesisService()
        result = await job.generate_examples(request, job_name, is_demo=False, )
        return result
    except Exception as e:
        print(f"Error in synthesis: {e}")
        raise

if __name__ == "__main__":
    try:
      
        print(sys.argv[1], '\n')
        print(sys.argv)
        file_name = sys.argv[1]  # Get filename from arguments

        # Read JSON file
        with open(file_name, 'r') as f:
            params = json.load(f)
        
        job_name = params.pop('job_name') 
        print(params)
        os.remove(file_name)
        request = SynthesisRequest.model_validate(params)
        # Get current loop or create new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result = loop.run_until_complete(run_synthesis(request, job_name))
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)