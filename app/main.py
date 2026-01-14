import asyncio
import sys
from loguru import logger
from app.db.engine import init_db

# Главная асинхронная функция
async def main():
    logger.info("Comment Sniper MVP is starting...")
    
    # 1. Инициализация Базы Данных
    logger.info("Initializing Database...")
    await init_db()
    logger.success("Database initialized successfully!")

    # Тут пока всё. Бот не запускаем, просто проверяем базу.

if __name__ == "__main__":
    # Запускаем асинхронный цикл
    if sys.platform == "win32":
        # Специфичный фикс для Windows, чтобы асинхронность работала стабильно
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())