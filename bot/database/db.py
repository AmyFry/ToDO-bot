import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

# 1. Пытаемся получить DATABASE_URL
database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Создаём движок для PostgreSQL
    engine = create_async_engine(database_url)
else:
    # 3. Если разработка локальная (на ПК), используем SQLite
    engine = create_async_engine('sqlite+aiosqlite:///todo.db')

# Создаём сессию
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)