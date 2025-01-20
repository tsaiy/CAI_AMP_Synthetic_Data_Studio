import subprocess
import os

composable_path = "/home/cdsw/synthetic-data-studio/build/shell_scripts/start_application.sh"
default_path  = "/home/cdsw/build/shell_scripts/start_application.sh"

# Choose the path based on the environment variable
if os.getenv("IS_COMPOSABLE"):
    script_path = composable_path
    os.chdir("/home/cdsw/synthetic-data-studio")
else:
    script_path = default_path

# Execute the script using the selected path
print(subprocess.run([f"bash {script_path}"], shell=True, check=True))

print("Application installed and should be running shortly")