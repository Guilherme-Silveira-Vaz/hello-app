from fastapi import FastAPI
import os
import socket
import time

app = FastAPI()
@app.get("/")
async def root():
 return {"message": "Hello World! Testando alterações em real time com CI/CD!"}


start_time = time.time()

@app.get("/status")
async def status():
    return {
        "status": "running",
        "version": os.getenv("APP_VERSION", "unknown"),
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - start_time, 2)
    }
