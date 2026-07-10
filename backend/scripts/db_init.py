"""
WoSafe Database Initialization
Creates all database tables and seeds them with development data.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set DATABASE_URL if not set
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./wosafe.db")

from sqlalchemy.ext.asyncio import create_async_engine
from app.database.base import Base
from scripts.seed_data import seed

async def init_db():
    print(f"Connecting to database at: {os.environ.get('DATABASE_URL')}")
    engine = create_async_engine(os.environ.get("DATABASE_URL"), echo=True)
    
    print("Dropping existing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Running seed script...")
    await seed()
    print("Database successfully initialized and seeded!")

if __name__ == "__main__":
    asyncio.run(init_db())
