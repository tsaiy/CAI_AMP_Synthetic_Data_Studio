# run_export_job.py

import subprocess
import sys
import os

if os.getenv("IS_COMPOSABLE"):
    
    os.chdir("/home/cdsw/synthetic-data-studio")

# def check_and_install_requirements():
#     """Check and install requirements from requirements.txt"""
#     # Get the current working directory instead of using __file__
#     current_dir = os.getcwd()
#     requirements_path = os.path.join(current_dir, 'requirements.txt')
    
#     if os.path.exists(requirements_path):
#         try:
#             print(f"Installing requirements from: {requirements_path}")
#             subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
#         except subprocess.CalledProcessError as e:
#             print(f"Error installing requirements: {e}")
#             sys.exit(1)
#     else:
#         print("No requirements.txt found, continuing with existing packages")

# # Run installation check at start
# check_and_install_requirements()

import sys
venv_path = os.path.join(os.path.dirname(os.path.abspath('')), '.venv/lib/python3.x/site-packages')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)


import sys
import json
from app.models.request_models import Export_synth

from app.services.export_results import Export_Service
import asyncio
import nest_asyncio  # Add this import

# Enable nested event loop
nest_asyncio.apply()

async def run_export(request):
    try:
        
        job = Export_Service()
        result = job.export(request)
        return result
    except Exception as e:
        print(f"Error in synthesis: {e}")
        raise

if __name__ == "__main__":
    try:
         
        #print(sys.argv)
        #print(os.environ)
        file_name = os.environ.get('file_name', '')  # Get filename from arguments

        # Read JSON file
        with open(file_name, 'r') as f:
            params = json.load(f)
        
         
        print(params)
        os.remove(file_name)
        request = Export_synth.model_validate(params)
        # Get current loop or create new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result = loop.run_until_complete(run_export(request))
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)