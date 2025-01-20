# #!/bin/bash
#!uvicorn main:app .port $CDSW_APP_PORT --server.address 127.0.0.1
# !streamlit run dev/app/frontend/streamlit_new_app.py --server.port $CDSW_APP_PORT --server.address 127.0.0.1

import subprocess
import os
import time
import sys

# Step 1: Start the Uvicorn server
uvicorn_process = subprocess.Popen(
    ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8081", "--reload"]
)
print("Started Uvicorn server.")

### Wait for a few seconds to ensure Uvicorn has started
#time.sleep(10)
## Start Streamlit
#port = int(os.getenv("CDSW_APP_PORT", "8081"))
## Step 2: Start the Streamlit app
#streamlit_process = subprocess.Popen(
#    ["streamlit", "run", "app/frontend/streamlit_new_app.py", "--server.port", str(port), "--server.address", "127.0.0.1"]
#)
#print("Started Streamlit app.")
#
## Optional: Wait for processes to complete or handle them as needed
#try:
#    uvicorn_process.wait()
#    streamlit_process.wait()
#except KeyboardInterrupt:
#    print("Terminating processes.")
#    uvicorn_process.terminate()
#    streamlit_process.terminate()
