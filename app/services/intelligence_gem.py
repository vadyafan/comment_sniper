import os
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai  # Библиотека для работы с файлами
from app.core.config import settings
# Убедись, что файл app/core/persona.py существует!
from app.core.persona import USER_PROFILE, STYLE_EXAMPLES 
from loguru import logger

# Настраиваем доступ к API для загрузки файлов
genai.configure(api_key=settings.GEMINI_API_KEY)

# --- СТРУКТУРА ДАННЫХ ---
class SnipeResult(BaseModel):
    detected_topic: str = Field(description="Main topic")
    relevance_score: int = Field(description="1-10 score")
    summary: str = Field(description="Brief summary")
    technical_context: str = Field(description="Technical explanation")
    rationale: str = Field(description="Why relevant")
    draft_insightful: str = Field(description="Draft 1")
    draft_provocative: str = Field(description="Draft 2")
    draft_additive: str = Field(description="Draft 3")

# --- МОЗГ ---
class AIBrain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )

    # 1. ТЕКСТОВЫЙ АНАЛИЗ (Для Снайпера)
    async def analyze_post(self, post_text: str) -> SnipeResult:
        logger.info("🧠 Brain analyzing text...")
        
        system_prompt = f"""
        {USER_PROFILE}
        
        Analyze this LinkedIn post for me based on my profile.
        OUTPUT format must be JSON matching the SnipeResult structure.
        """
        
        try:
            structured_llm = self.llm.with_structured_output(SnipeResult)
            return await structured_llm.ainvoke([("system", system_prompt), ("human", post_text)])
        except Exception as e:
            logger.error(f"Brain Text Error: {e}")
            # Возвращаем заглушку при ошибке
            return SnipeResult(
                detected_topic="Error", relevance_score=0, summary="Error",
                technical_context=str(e), rationale="Error",
                draft_insightful=".", draft_provocative=".", draft_additive="."
            )

    # 2. ГОЛОСОВОЙ АНАЛИЗ (Для Бота) <--- ВОТ ЭТОЙ ФУНКЦИИ НЕ ХВАТАЛО
    async def process_voice_reaction(self, audio_path: str, post_context: str) -> str:
        logger.info(f"🧠 Brain listening to voice: {audio_path}")
        
        try:
            # А. Загружаем файл в облако Google
            audio_file = genai.upload_file(path=audio_path, mime_type="audio/ogg")
            
            # Б. Формируем промпт
            prompt = f"""
            {USER_PROFILE}
            
            {STYLE_EXAMPLES}

            CONTEXT:
            I am looking at a LinkedIn post.
            POST CONTENT:
            "{post_context[:3000]}..."

            MY AUDIO REACTION (Russian):
            I have recorded a voice note with my thoughts.
            
            TASK:
            1. Listen to the audio.
            2. Extract my core arguments.
            3. Write a high-quality LinkedIn comment in English based on my thoughts.
            4. MIMIC my style from the examples (tone, casing).
            
            OUTPUT ONLY THE COMMENT TEXT.
            """

            # В. Отправляем в модель
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content([prompt, audio_file])
            
            return response.text

        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return f"⚠️ I couldn't process the audio. Error: {e}"

brain = AIBrain()