import subprocess
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path.cwd()

# Add project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Import PathManager
from app.core.path_manager import PathManager
path_manager = PathManager()

# Initialize PathManager
path_manager = PathManager()

# Main execution
with path_manager.in_project_directory():
    # Execute the start application script
    subprocess.run(["bash build/shell_scripts/start_application.sh"], shell=True, check=True)

print("Application running")