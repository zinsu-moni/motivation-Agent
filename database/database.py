from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from models.models import Base
import logging

logger = logging.getLogger(__name__)
Env = load_dotenv()

if Env["DATABASE_URL"].startswith("sqlite://"):
    ASYNC_DATABASE_URL = Env["DATABASE_URL"].replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = Env["DATABASE_URL"]


engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  
    future=True
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    await engine.dispose()