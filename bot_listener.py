import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from app.core.config import settings
from app.services.intelligence_gem import brain

# --- ГЛОБАЛЬНАЯ ПАМЯТЬ ---
# Сюда мы будем класть текст последнего поста.
# В идеале нужна БД (Redis), но для одного пользователя сойдет файл.
LAST_POST_FILE = "data/last_post.txt"

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 1. ХЕНДЛЕР: Принимаем голосовое сообщение
@dp.message(F.voice)
async def handle_voice(message: Message):
    user_id = message.from_user.id
    if str(user_id) != settings.TELEGRAM_CHAT_ID:
        return # Игнорируем чужаков

    logger.info("🎙️ Received voice message!")
    await message.answer("👂 Слушаю и формулирую...")

    # 1. Проверяем, есть ли контекст (пост)
    if not os.path.exists(LAST_POST_FILE):
        await message.answer("⚠️ Я не помню последний пост. Сначала пришли мне пост через Снайпера.")
        return

    with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
        post_text = f.read()

    # 2. Скачиваем файл
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = f"data/voice_{file_id}.ogg"
    
    await bot.download_file(file.file_path, file_path)

    # 3. Отправляем в Brain
    try:
        comment_draft = await brain.process_voice_reaction(file_path, post_text)
        
        # 4. Отправляем ответ
        response_text = (
            f"✅ <b>Draft generated:</b>\n\n"
            f"<code>{comment_draft.strip()}</code>"
        )
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    finally:
        # Чистим за собой
        if os.path.exists(file_path):
            os.remove(file_path)

# 2. ХЕНДЛЕР: Обычный текст (на всякий случай)
@dp.message(F.text)
async def handle_text(message: Message):
    if str(message.from_user.id) == settings.TELEGRAM_CHAT_ID:
        await message.answer("🎤 Запиши голосовое, чтобы прокомментировать последний пост.")

async def main():
    logger.info("🎧 Bot Listener started. Waiting for voice...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())