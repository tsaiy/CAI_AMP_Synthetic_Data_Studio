import uvicorn
import os

DEV_SERVER_PORT = 8100

if __name__ == "__main__":
    port = int(os.getenv("CDSW_APP_PORT", DEV_SERVER_PORT))
    uvicorn.run(
      "main:app",
      host="127.0.0.1",
      port=port,
      reload=True
)
