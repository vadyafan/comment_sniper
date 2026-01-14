import asyncio
import sys
from dataclasses import dataclass
from app.services.notifier import notifier

# Эмулируем ответ от нового Brain.py
@dataclass
class FakeSniperResult:
    detected_topic: str = "Modern Data Stack"
    relevance_score: int = 9
    
    # Вот эти поля ты просил:
    summary: str = "Автор сравнивает Databricks и Snowflake, утверждая, что Databricks выигрывает в ML задачах."
    technical_context: str = "В посте упоминается 'Lakehouse architecture'. Это концепция объединения Data Lake (гибкость) и Data Warehouse (структура). Автор делает упор на то, что для Data Engineering задач Python-first подход Databricks удобнее, чем SQL-first подход Snowflake."
    
    rationale: str = "Высокая релевантность для DE."
    draft_insightful: str = "Totally agree regarding the Python-first approach flexibility."
    draft_provocative: str = "But isn't Snowflake catching up fast with Snowpark?"
    draft_additive: str = "We recently migrated to Lakehouse and saw 30% perf boost."

async def test_html_sending():
    print("🎨 Запускаю тест новой верстки (Summary + Explanation)...")
    
    fake_result = FakeSniperResult()
    fake_url = "https://www.linkedin.com/feed/update/urn:li:activity:TEST_123/"

    try:
        await notifier.send_report(fake_result, fake_url)
        print("✅ Сообщение отправлено! Проверяй Telegram.")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
    finally:
        await notifier.close()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(test_html_sending())