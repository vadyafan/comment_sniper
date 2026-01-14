from typing import Optional
from enum import Enum
from datetime import datetime
from sqlmodel import Field, SQLModel

# 1. ENUMS (Справочники из твоего отчета)
class TargetQuadrant(str, Enum):
    AGENTIC_VANGUARD = "Agentic Vanguard"
    DE_REALISTS = "DE Realists"
    STARTUP_CTO = "Startup CTO"
    GOVERNANCE = "Governance & Enterprise"

class DiscussionVector(str, Enum):
    DE_IS_DEAD = "DE is Dead / Identity Crisis"
    RAG_VS_FT = "RAG vs Fine-Tuning"
    VECTOR_VS_POSTGRES = "Vector DB vs Postgres"
    RUST_VS_PYTHON = "Rust vs Python"
    AGENT_RELIABILITY = "Agent Reliability Gap"
    GENERAL = "General Tech"

# 2. TABLES (Таблицы)

class Influencer(SQLModel, table=True):
    """Таблица целевых персон (Top-50)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    linkedin_url: str = Field(unique=True, index=True) # Уникальный URL профиля
    quadrant: TargetQuadrant # К какой группе относится
    notes: Optional[str] = None # Твои заметки
    is_active: bool = Field(default=True) # Чтобы можно было отключать мониторинг

class Post(SQLModel, table=True):
    """Таблица найденных постов"""
    id: Optional[int] = Field(default=None, primary_key=True)
    influencer_id: int = Field(foreign_key="influencer.id") # Связь с автором
    original_url: str = Field(unique=True) # Чтобы не обрабатывать пост дважды
    content_text: str  # Полный текст поста
    detected_vector: DiscussionVector = Field(default=DiscussionVector.GENERAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)