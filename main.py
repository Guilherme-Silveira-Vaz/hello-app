from fastapi import FastAPI
app = FastAPI()
@app.get("/")
async def root():
 return {"message": "Hello World! Testando alterações em real time com CI/CD!"}
