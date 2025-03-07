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

# Ensure uv is installed
def ensure_uv_installed():
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["curl -LsSf https://astral.sh/uv/install.sh | sh"], shell=True, check=True)
        os.environ["PATH"] = f"{os.environ['HOME']}/.cargo/bin:{os.environ['PATH']}"

# Setup virtual environment and dependencies
def setup_environment():
    # project_root = path_manager.root_dir
    # print("path_root: ", project_root)
    venv_dir = PROJECT_ROOT / ".venv"
    
    # Create venv if it doesn't exist - specifying the path explicitly
    if not venv_dir.exists():
        subprocess.run(["uv", "venv", ".venv"], cwd=PROJECT_ROOT, check=True)
    
    # Install dependencies with uv pip instead of sync to avoid pyproject.toml parsing issues
    subprocess.run(["uv", "pip", "install", "-e", "."], cwd=PROJECT_ROOT, check=True)

# Main execution
with path_manager.in_project_directory():
    # Ensure uv is installed
    ensure_uv_installed()
    
    # Setup virtual environment and dependencies
    setup_environment()
    
    # Execute the build client script
    subprocess.run(["bash build/shell_scripts/build_client.sh"], shell=True, check=True)

print("Client application built successfully")