import asyncio
import sys



from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession  # важно
from app.db.engine import engine, init_db
from app.db.models import Influencer, TargetQuadrant

# Данные из твоего Deep Research
initial_influencers = [
    # --- Quadrant 1: Agentic Vanguard ---
    {"name": "Harrison Chase", "url": "https://www.linkedin.com/in/harrison-chase-961287118/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},
    {"name": "Joao Moura", "url": "https://www.linkedin.com/in/joaomdmoura/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},
    {"name": "Jerry Liu", "url": "https://www.linkedin.com/in/jerry-liu-64390071/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},
    {"name": "Andrew Ng", "url": "https://www.linkedin.com/in/andrewyng/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},
    {"name": "Allie K. Miller", "url": "https://www.linkedin.com/in/alliekmiller/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},
    {"name": "Chip Huyen", "url": "https://www.linkedin.com/in/chiphuyen/", "quadrant": TargetQuadrant.AGENTIC_VANGUARD},

    # --- Quadrant 2: DE Realists ---
    {"name": "Joe Reis", "url": "https://www.linkedin.com/in/joereis/", "quadrant": TargetQuadrant.DE_REALISTS},
    {"name": "Barr Moses", "url": "https://www.linkedin.com/in/barrmoses/", "quadrant": TargetQuadrant.DE_REALISTS},
    {"name": "Ben Rogojan", "url": "https://www.linkedin.com/in/benjaminsrogojan/", "quadrant": TargetQuadrant.DE_REALISTS},
    {"name": "Chad Sanderson", "url": "https://www.linkedin.com/in/chad-sanderson/", "quadrant": TargetQuadrant.DE_REALISTS},
    {"name": "Zach Wilson", "url": "https://www.linkedin.com/in/zachwilson12/", "quadrant": TargetQuadrant.DE_REALISTS},
    
    # --- Quadrant 3: Startup CTOs ---
    {"name": "Andrew Bihl", "url": "https://www.linkedin.com/in/andrewbihl/", "quadrant": TargetQuadrant.STARTUP_CTO},
    {"name": "Florian Juengermann", "url": "https://www.linkedin.com/in/florianjuengermann/", "quadrant": TargetQuadrant.STARTUP_CTO},
    {"name": "Yo Shibata", "url": "https://www.linkedin.com/in/yoshibata/", "quadrant": TargetQuadrant.STARTUP_CTO},

    # --- Quadrant 4: Governance ---
    {"name": "Pascal Bornet", "url": "https://www.linkedin.com/in/pascalbornet/", "quadrant": TargetQuadrant.GOVERNANCE},
    {"name": "Bernard Marr", "url": "https://www.linkedin.com/in/bernardmarr/", "quadrant": TargetQuadrant.GOVERNANCE},
]

async def seed_data():
    print("🌱 Starting database seeding...")

    await init_db()  

    async with AsyncSession(engine) as session:
        for data in initial_influencers:
            statement = select(Influencer).where(
                Influencer.linkedin_url == data["url"]
            )
            results = await session.exec(statement)
            existing_user = results.first()

            if not existing_user:
                new_influencer = Influencer(
                    name=data["name"],
                    linkedin_url=data["url"],
                    quadrant=data["quadrant"],
                )
                session.add(new_influencer)
                print(f"   Writing: {data['name']}")
            else:
                print(f"   Skipping (already exists): {data['name']}")

        await session.commit()

    print("✅ Seeding complete!")


if __name__ == "__main__":
    # на Python 3.14+ лучше без WindowsSelectorEventLoopPolicy (оно deprecated)
    try:
        asyncio.run(seed_data())
    finally:
        # важно для Windows + aiosqlite: закрыть пул/соединения
        asyncio.run(engine.dispose())