import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Generator MVP",
    description="MVP веб-платформы для генерации документов с AI",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Привет! Это MVP Document Generator!", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Приложение работает!"}