from fastapi import FastAPI, Response
import os
import socket
import time

app = FastAPI()

start_time = time.time()

@app.get("/")
def root():
    return {"message": "Hello World! Testando alterações em CI/CD em tempo real!"}

@app.get("/status")
def status():
    version = os.getenv("APP_VERSION", "unknown")
    hostname = socket.gethostname()
    uptime = round(time.time() - start_time, 2)

    html = f"""
    <html>
        <head>
            <title>Status da Aplicação</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #0d1117;
                    color: #e6edf3;
                    text-align: center;
                    padding: 40px;
                }}
                .card {{
                    background-color: #161b22;
                    padding: 30px;
                    border-radius: 12px;
                    width: 400px;
                    margin: 0 auto;
                    box-shadow: 0 0 12px rgba(255,255,255,0.08);
                }}
                h1 {{
                    color: #58a6ff;
                    margin-bottom: 20px;
                }}
                .item {{
                    margin: 10px 0;
                    font-size: 18px;
                }}
                .label {{
                    color: #8b949e;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Status da Aplicação</h1>
                <div class="item"><span class="label">Status:</span> running ✔️</div>
                <div class="item"><span class="label">Versão:</span> {version}</div>
                <div class="item"><span class="label">Hostname:</span> {hostname}</div>
                <div class="item"><span class="label">Uptime:</span> {uptime} segundos</div>
            </div>
        </body>
    </html>
    """

    return Response(content=html, media_type="text/html")
