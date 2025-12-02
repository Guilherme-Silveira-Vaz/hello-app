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
 
@app.get("/status-ui", response_class=HTMLResponse)
async def status_ui():
    return """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Status da Aplicação</title>

<style>
    body {
        margin: 0;
        font-family: Arial, Helvetica, sans-serif;
        background: linear-gradient(135deg, #2b5876, #4e4376);
        color: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    .card {
        background: rgba(255, 255, 255, 0.12);
        padding: 25px 35px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        width: 350px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    h1 {
        margin-bottom: 10px;
        font-size: 26px;
        font-weight: 600;
    }

    .item {
        margin: 12px 0;
        font-size: 18px;
    }

    .label {
        font-weight: bold;
    }

    .footer {
        margin-top: 20px;
        font-size: 14px;
        opacity: 0.8;
    }
</style>

</head>
<body>

<div class="card">
    <h1>Status da Aplicação</h1>

    <div class="item"><span class="label">Status:</span> <span id="status">--</span></div>
    <div class="item"><span class="label">Versão:</span> <span id="version">--</span></div>
    <div class="item"><span class="label">Hostname:</span> <span id="hostname">--</span></div>
    <div class="item"><span class="label">Uptime:</span> <span id="uptime">--</span> s</div>

    <div class="footer">Atualiza automaticamente</div>
</div>

<script>
async function loadStatus() {
    try {
        const res = await fetch("/status");
        const data = await res.json();

        document.getElementById("status").textContent = data.status;
        document.getElementById("version").textContent = data.version;
        document.getElementById("hostname").textContent = data.hostname;
        document.getElementById("uptime").textContent = data.uptime_seconds;
    } catch (e) {
        document.getElementById("status").textContent = "erro";
    }
}

// Atualiza a cada 2 segundos
setInterval(loadStatus, 2000);
loadStatus();
</script>

</body>
</html>
    """
