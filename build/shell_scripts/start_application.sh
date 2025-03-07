#!/bin/bash
set -eox pipefail

# We're already in the project root directory thanks to PathManager
# Activate virtual environment
source .venv/bin/activate
python app/run.py