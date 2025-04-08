from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.settings import Settings

settings = Settings()
print("DATABASE_URL:", settings.DATABASE_URL)
async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
