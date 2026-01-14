import asyncio
import sys
from app.services.intelligence_gem import brain
from loguru import logger

# Текст, который мы только что "украли" у NVIDIA (имитация)
MOCK_TEXT = """
Yesterday at NVIDIA Live at CES 2026 CEO Jensen Huang shared how AI is transforming every domain and device, redefining the future of computing.
He unveiled the Rubin platform, a new extreme-scale AI supercomputer architecture now in production, alongside major advances in open models and autonomous driving.
Catch up on all the announcements.
"""

async def test():
    logger.info("🧠 Testing Intelligence Layer...")
    
    result = await brain.analyze_post(MOCK_TEXT, author_name="Jensen Huang (NVIDIA)")
    
    if result:
        print("\n" + "="*50)
        print(f"🎯 TOPIC: {result.detected_topic.upper()} (Score: {result.relevance_score}/10)")
        print("="*50)
        print(f"📝 SUMMARY: {result.summary}\n")
        
        print(f"💡 INSIGHTFUL: {result.draft_insightful}\n")
        print(f"🌶️ PROVOCATIVE: {result.draft_provocative}\n")
        print(f"➕ ADDITIVE: {result.draft_additive}\n")
        
        print("-" * 20)
        print(f"🤔 RATIONALE: {result.rationale}")
        print("="*50)
    else:
        logger.error("Failed to generate insights.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())