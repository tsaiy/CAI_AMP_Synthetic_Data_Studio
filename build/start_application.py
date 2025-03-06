import subprocess
import os
import sys
from pathlib import Path

# Add app directory to path so we can import the PathManager
sys.path.append(str(Path(__file__).parent.parent))
from app.core.path_manager import PathManager

# Initialize PathManager
path_manager = PathManager()

# Main execution
with path_manager.in_project_directory():
    # Execute the start application script
    subprocess.run(["bash build/shell_scripts/start_application.sh"], shell=True, check=True)

print("Application running")