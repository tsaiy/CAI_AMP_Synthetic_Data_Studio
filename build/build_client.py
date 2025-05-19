import subprocess
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd()

# Check if we're in a composable environment
if os.getenv("IS_COMPOSABLE"):
    # If composable, change to the specified directory
    PROJECT_ROOT = Path("/home/cdsw/synthetic-data-studio")
else:
    # Otherwise, use the current directory as the project root
    PROJECT_ROOT = Path.cwd()
    
# Add project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Import PathManager
from app.core.path_manager import PathManager
path_manager = PathManager()

# Main execution - just call the shell script that does everything
with path_manager.in_project_directory():
    # Execute the comprehensive build client script
    subprocess.run(["bash build/shell_scripts/build_client.sh"], shell=True, check=True)

print("Client application built successfully")