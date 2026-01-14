from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Определяем корень проекта, чтобы знать, где лежат данные
PROJECT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_DIR / "data"

class Settings(BaseSettings):
    # Тут перечисляем переменные, которые ожидаем увидеть в .env
    OPENAI_API_KEY: str = "sk-..." # Заглушка, чтобы не падало, если ключа нет
    TELEGRAM_BOT_TOKEN: str = "123:ABC..."
    GEMINI_API_KEY: str = "AIzaSyBb-zxI-o11mAmaHCRG7hJ-cthkRacSxwk"
    TELEGRAM_CHAT_ID: str = 373043879
    # Путь к базе данных (SQLite файл)
    # sqlite+aiosqlite означает, что мы используем асинхронный драйвер
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/sniper.db"

    # Магия pydantic: читать файл .env в кодировке utf-8
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Создаем единственный экземпляр настроек, который будем импортировать везде
settings = Settings()