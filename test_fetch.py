import asyncio
import sys
from app.services.fetcher import fetcher
from loguru import logger

# Ссылка на реальный пост (Harrison Chase про AI Agents)
# Если ссылка устареет, скрипт просто вернет 404, но механизм мы проверим.
TEST_URL = "https://www.linkedin.com/posts/nvidia_yesterday-at-nvidia-live-at-ces-2026-ceo-activity-7414368372374556672-QjeX?utm_source=share&utm_medium=member_desktop&rcm=ACoAACQjXVsBdyqEOHWHUbBGjWUSYrhEKonxECI"



async def test():
    logger.info(f"🚀 Starting Smoke Test on URL: {TEST_URL}")
    
    # Запускаем наш фетчер
    content = await fetcher.fetch_post_text(TEST_URL)
    
    if content:
        print("\n" + "="*50)
        print("✅ RAW CONTENT PREVIEW (First 500 chars):")
        print("="*50)
        # Печатаем первые 500 символов, чтобы убедиться, что это не пустота
        print(content[:500])
        print("="*50 + "\n")
        
        # Простая проверка: попали ли мы на страницу логина
        if "Join LinkedIn" in content or "Sign in" in content[:200]:
            logger.warning("⚠️ Warning: LinkedIn redirected to Login Page (Auth Wall).")
            logger.info("Solution: We might need cookies for full access, but let's see if the post text is visible below.")
        else:
            logger.success("🎉 Success! Looks like valid page content.")
            
    else:
        logger.error("❌ Failed to fetch content (Result is None).")

if __name__ == "__main__":
    asyncio.run(test())