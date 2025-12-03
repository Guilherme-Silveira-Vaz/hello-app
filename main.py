from fastapi import FastAPI, Response
import os
import socket
import time

app = FastAPI()

start_time = time.time()

@app.get("/")
def home():
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <title>Minha Aplicação FastAPI</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: "Segoe UI", sans-serif;
            }

            body {
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                height: 100vh;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                animation: fadein 1.2s ease;
            }

            @keyframes fadein {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .container {
                background: rgba(255, 255, 255, 0.07);
                backdrop-filter: blur(12px);
                border-radius: 18px;
                padding: 40px;
                width: 100%;
                max-width: 780px;
                box-shadow: 0 0 25px rgba(0,0,0,0.4);
                border: 1px solid rgba(255,255,255,0.15);
                animation: slideup 0.8s ease;
            }

            @keyframes slideup {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            h1 {
                font-size: 2.6rem;
                text-align: center;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }

            p.subtitle {
                text-align: center;
                font-size: 1.1rem;
                opacity: 0.85;
                margin-bottom: 30px;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-top: 25px;
            }

            .card {
                background: rgba(255, 255, 255, 0.12);
                padding: 20px;
                border-radius: 14px;
                text-align: center;
                transition: 0.25s ease;
                border: 1px solid rgba(255,255,255,0.1);
            }

            .card:hover {
                background: rgba(255, 255, 255, 0.18);
                transform: translateY(-4px);
                box-shadow: 0 8px 18px rgba(0,0,0,0.3);
            }

            footer {
                text-align: center;
                margin-top: 35px;
                font-size: 0.9rem;
                opacity: 0.65;
            }

        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Nova Versão da Aplicação</h1>
            <p class="subtitle">Deploy automático aplicado com sucesso via CI/CD + ArgoCD</p>

            <div class="grid">
                <div class="card">
                    <div class="card-title">🔄 Build Automatizado</div>
                    <div class="card-text">
                        A imagem Docker foi gerada automaticamente pelo GitHub Actions.
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">📦 Novo Container</div>
                    <div class="card-text">
                        O ArgoCD detectou a nova versão e atualizou o cluster.
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">⚡ Zero Downtime</div>
                    <div class="card-text">
                        Sua aplicação permaneceu online durante todo o processo.
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">🎨 Nova Interface</div>
                    <div class="card-text">
                        A mudança visual prova que a nova versão chegou em produção.
                    </div>
                </div>
            </div>

            <footer>
                Versão 2.0 — Deploy demonstrativo para apresentação DevOps
            </footer>
        </div>
    </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

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
