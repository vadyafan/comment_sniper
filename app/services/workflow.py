import asyncio
from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.services.notifier import notifier

from app.db.engine import engine
from app.db.models import Post, Influencer, DiscussionVector
from app.services.fetcher import fetcher
from app.services.intelligence_gem import brain
from app.services.gmail import gmail_service

class SniperWorkflow:
    async def process_url(self, url: str, source: str = "manual"):
        """
        Главная логика: URL -> Text -> AI -> DB
        """
        logger.info(f"🔫 Processing Target: {url} (Source: {source})")

        # 1. Проверка дублей (Deduplication)
        # Если мы уже обрабатывали этот пост — пропускаем
        async with AsyncSession(engine) as session:
            statement = select(Post).where(Post.original_url == url)
            existing = await session.exec(statement)
            if existing.first():
                logger.warning(f"⚠️ Post already processed: {url}")
                return

        # 2. Fetching (Скрапинг)
        text_content = await fetcher.fetch_post_text(url)
        if not text_content or len(text_content) < 50:
            logger.error("❌ Failed to fetch content or content too short.")
            return

        # 3. Intelligence (Анализ AI)
        # Для MVP пока не ищем автора в базе, просто пишем Unknown
        ai_result = await brain.analyze_post(text_content)
        
        if not ai_result:
            logger.error("❌ AI returned None.")
            return

        # 4. Saving (Сохранение в БД)
        logger.info("💾 Saving results to Database...")
        async with AsyncSession(engine) as session:
            # Сначала найдем или создадим "Generic" инфлюенсера для тестов
            # (В реале тут будет поиск по URL профиля)
            
            # Создаем запись о посте
            new_post = Post(
                influencer_id=1, # Пока хардкод ID=1 (Harrison Chase) для теста
                original_url=url,
                content_text=text_content[:3000], # Обрезаем для экономии места
                detected_vector=DiscussionVector.GENERAL # AI может вернуть строку, тут можно маппить
            )
            session.add(new_post)
            await session.commit()
            await session.refresh(new_post)
            
            # В будущем: тут сохраним и CommentDraft
        await notifier.send_report(ai_result, url, text_content)
        # 5. Output (Пока в консоль, потом в Telegram)
        self._print_report(ai_result, url)

    def _print_report(self, res, url):
        print("\n" + "="*60)
        print(f"🔥 SNIPER REPORT for {url}")
        print("="*60)
        print(f"🎯 TOPIC: {res.detected_topic} (Score: {res.relevance_score})")
        print(f"📝 SUMMARY: {res.summary}")
        print("-" * 30)
        print(f"1️⃣ INSIGHTFUL: {res.draft_insightful}")
        print("-" * 30)
        print(f"2️⃣ PROVOCATIVE: {res.draft_provocative}")
        print("-" * 30)
        print(f"3️⃣ ADDITIVE: {res.draft_additive}")
        print("="*60 + "\n")

    async def run_cycle(self):
        """Полный цикл проверки почты"""
        logger.info("🔄 Starting Auto-Cycle...")
        
        # 1. Проверяем почту
        urls = gmail_service.check_for_linkedin_emails()
        
        if not urls:
            logger.info("💤 No new tasks.")
            return

        # 2. Обрабатываем каждый URL
        for url in urls:
            await self.process_url(url, source="gmail")

# Singleton
workflow = SniperWorkflow()