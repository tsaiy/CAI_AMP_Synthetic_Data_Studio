#!/usr/bin/bash
set -eox pipefail

python -m pip install -r requirements.txt
python app/run.py
