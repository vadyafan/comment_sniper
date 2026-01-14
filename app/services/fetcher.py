import asyncio
from camoufox.async_api import AsyncCamoufox
from loguru import logger

class LinkedInFetcher:
    """
    Отвечает за безопасный обход LinkedIn через Camoufox (Headless Firefox).
    Пытается имитировать обычного пользователя.
    """
    
    async def fetch_post_text(self, url: str) -> str | None:
        logger.info(f"🕸️ Fetching URL: {url}")
        
        # Запускаем браузер с защитой от детекта
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
            
            try:
                # 1. Переходим на страницу
                # wait_until="domcontentloaded" значит "не жди все картинки, грузи только текст"
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # 2. Небольшая пауза для имитации человека и подгрузки JS
                await asyncio.sleep(3)
                
                # 3. Пытаемся найти текст поста
                # Селектор может меняться, для MVP берем самый широкий контейнер описания
                # Обычно текст поста лежит в .feed-shared-update-v2__description
                # Или в public profile: .core-section-container
                
                # Пробуем получить весь текст страницы для анализа LLM
                # (LLM сама разберется, где там мусор, а где пост)
                content = await page.content()
                
                # В идеале тут нужен BeautifulSoup для очистки HTML от тегов,
                # но пока вернем "грязный" текст или `innerText` body
                text_content = await page.evaluate("document.body.innerText")
                
                logger.success(f"✅ Successfully fetched {len(text_content)} chars")
                return text_content

            except Exception as e:
                logger.error(f"❌ Error fetching post: {e}")
                return None

# Singleton instance (один экземпляр на приложение)
fetcher = LinkedInFetcher()