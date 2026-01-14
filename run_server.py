import uvicorn
import sys
import asyncio
from loguru import logger

if __name__ == "__main__":
    # --- WINDOWS FIX ---
    # Принудительно ставим Proactor, чтобы Playwright мог запускать браузер.
    # Это должно быть выполнено ДО запуска любого асинхронного цикла.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # -------------------

    print("🕸️ Starting Comment Sniper Web Server...")
    print("✅ Listening for signals on http://localhost:8000")
    
    # ВАЖНО: reload=False
    # С включенным reload создается новый процесс, который теряет настройку set_event_loop_policy.
    uvicorn.run("app.web:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")