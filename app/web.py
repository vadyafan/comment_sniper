from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.workflow import workflow
from app.db.engine import init_db
from loguru import logger

# 1. Создаем приложение
app = FastAPI(title="Comment Sniper API")

# 2. Настраиваем CORS (Разрешаем браузеру стучаться к нам)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых сайтов (включая linkedin.com)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Модель данных (что мы ждем от браузера)
class WebhookPayload(BaseModel):
    url: str
    source: str = "browser_parasite"

# 4. Событие старта (Инициализация БД)
@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("🚀 Sniper API started. Waiting for signals...")

# 5. Эндпоинт (Сюда браузер будет слать данные)
@app.post("/webhook/process")
async def process_post(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Принимает URL и отправляет его в обработку в фоне,
    чтобы не заставлять браузер ждать ответа.
    """
    logger.info(f"📨 Signal received from Browser: {payload.url}")
    
    # Запускаем workflow в фоне (Fire and Forget)
    background_tasks.add_task(workflow.process_url, payload.url, payload.source)
    
    return {"status": "accepted", "message": "Processing started"}

@app.get("/")
def health_check():
    return {"status": "alive", "system": "Comment Sniper"}