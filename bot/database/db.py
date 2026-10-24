from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    # Имя таблицы будет зависеть от названия класса модели. 
    # Однако всегда можно задать другое имя таблицы, переобределив занчение из класса.
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

# Здесь указываю, где лежит бд. /// - база будет работать в корне проекта, откуда бы ни запускался бот.
engine = create_async_engine('sqlite+aiosqlite:///todo.db')

# Создаю сессии. expire_on_commit=False нужен для того, чтобы можно было прочитать поля объектов.
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)