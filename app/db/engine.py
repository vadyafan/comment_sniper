from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from app.core.config import settings

# Создаем движок, используя URL из конфига
engine = create_async_engine(settings.DATABASE_URL, echo=True) 
# echo=True будет выводить все SQL запросы в консоль (удобно для отладки)

async def init_db():
    """Эта функция создаст файл базы данных и все таблицы, если их нет"""
    async with engine.begin() as conn:
        # Аналог CREATE TABLE IF NOT EXISTS для всех моделей
        await conn.run_sync(SQLModel.metadata.create_all)