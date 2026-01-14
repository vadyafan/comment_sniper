import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.core.config import settings
from loguru import logger

# Путь к файлу "памяти"
LAST_POST_FILE = "data/last_post.txt"

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.chat_id = settings.TELEGRAM_CHAT_ID

    async def send_report(self, snipe_result, url, full_text_content: str): # <--- Добавили аргумент full_text
        logger.info("📲 Sending report...")
        
        # 1. СОХРАНЯЕМ КОНТЕКСТ ДЛЯ БОТА
        # Создаем папку data если нет
        os.makedirs("data", exist_ok=True)
        with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
            f.write(full_text_content)
        
        # 2. Формируем сообщение
        message = (
            f"🔥 <b>SNIPER ALERT</b>\n"
            f"🔗 <a href='{url}'>LinkedIn Post</a>\n\n"
            f"📝 <b>Summary:</b> <i>{snipe_result.summary}</i>\n\n"
            f"💡 <b>Context:</b> {snipe_result.technical_context}\n\n"
            f"🎙️ <b>Action:</b> Запиши войс, чтобы ответить!"
        )

        # Отправляем черновики (на всякий случай, вдруг лень говорить)
        drafts = (
             f"\n👇 <b>Auto-Drafts:</b>\n"
             f"1️⃣ <code>{snipe_result.draft_insightful}</code>\n"
             f"2️⃣ <code>{snipe_result.draft_provocative}</code>"
        )

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message + drafts, disable_web_page_preview=True)
            logger.success("✅ Telegram notification sent!")
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            
    async def close(self):
        await self.bot.session.close()

notifier = TelegramNotifier()