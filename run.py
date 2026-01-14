import asyncio
import sys
from loguru import logger
from app.services.workflow import workflow
from app.db.engine import init_db

async def main():
    # Инициализируем базу при старте
    await init_db()
    
    print("\n🔫 COMMENT SNIPER MVP v1.0")
    print("1. Manual Mode (Вставить ссылку)")
    print("2. Auto Mode (Проверить Gmail)")
    print("3. Exit")
    
    choice = input("Select mode (1/2/3): ")
    
    if choice == "1":
        url = input("Paste LinkedIn Post URL: ").strip()
        if url:
            await workflow.process_url(url, source="manual")
    
    elif choice == "2":
        await workflow.run_cycle()
        
    elif choice == "3":
        print("Bye!")
        return
    else:
        print("Invalid choice")

if __name__ == "__main__":
    #if sys.platform == "win32":
    #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())