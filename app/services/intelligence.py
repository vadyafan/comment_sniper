import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from app.core.config import settings

# 1. Определяем структуру ответа (Schema)
# Это гарантирует, что LLM вернет не просто текст, а поля, готовые для БД.
class SnipeResult(BaseModel):
    detected_topic: str = Field(description="Определенный дискуссионный вектор (например: 'RAG vs FT', 'DE is Dead', 'General AI').")
    summary: str = Field(description="Краткая выжимка поста (1-2 предложения). В чем тезис автора?")
    
    # Три стратегии комментирования
    draft_insightful: str = Field(description="Комментарий 'Second-order insight'. Глубокая мысль, развивающая тему.")
    draft_provocative: str = Field(description="Вежливый челлендж. Вопрос 'А что если?' или альтернативный взгляд.")
    draft_additive: str = Field(description="Дополнение личным опытом или фактом (Data Contracts, FinOps, GPU costs).")
    
    rationale: str = Field(description="Почему были выбраны именно эти углы атаки (Chain of Thought).")
    relevance_score: int = Field(description="Оценка от 1 до 10: насколько этот пост подходит для тех-дискуссии.")

# 2. Настраиваем клиента
# instructor патчит стандартный клиент OpenAI, добавляя магию валидации
client = instructor.from_openai(AsyncOpenAI(api_key=settings.OPENAI_API_KEY))

class IntelligenceService:
    async def analyze_post(self, raw_text: str, author_name: str = "Unknown") -> SnipeResult:
        """
        Анализирует текст поста и генерирует варианты комментариев.
        """
        
        system_prompt = """
        Ты — Senior Tech Architect и Data Engineer с глубоким пониманием индустрии.
        Твоя цель — писать осмысленные, профессиональные комментарии для LinkedIn.
        
        ТВОИ ПРИНЦИПЫ:
        1. NO FLUFF: Запрещены фразы "Great post!", "Thanks for sharing", "Delve", "In today's world".
        2. BE SPECIFIC: Если речь про базы данных, упоминай Postgres/Vector DB. Если про AI — RAG/Fine-Tuning.
        3. TONE: Профессиональный, инженерный, лаконичный. Без эмодзи-спама.
        
        CONTEXT (Дискуссионные векторы 2025-2026):
        - DE is Dead? (Сдвиг от пайплайнов к архитектуре и FinOps)
        - RAG vs Fine-Tuning (RAG для фактов, FT для стиля)
        - Vector DB vs Postgres (Pgvector побеждает для <100M векторов)
        - Agents Reliability (Проблема эвалов и мониторинга)
        
        Задача: Проанализируй текст и выдай 3 варианта ответа в строгом JSON формате.
        """

        try:
            # Вызов LLM с форсированием схемы (response_model)
            resp = await client.chat.completions.create(
                model="gpt-4o", # Или gpt-3.5-turbo, если хочешь дешевле для тестов
                response_model=SnipeResult,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"AUTHOR: {author_name}\n\nPOST CONTENT:\n{raw_text[:4000]}"} 
                    # Обрезаем до 4000 символов, чтобы не перегрузить контекст мусором
                ],
                temperature=0.7,
            )
            return resp
            
        except Exception as e:
            # Если ошибка (например, кончились деньги на API), возвращаем пустой результат
            print(f"❌ LLM Error: {e}")
            return None

# Singleton
brain = IntelligenceService()