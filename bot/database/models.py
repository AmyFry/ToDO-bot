from datetime import datetime
from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, String, Boolean, DateTime, func

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    user_name: Mapped[str | None] = mapped_column()

    categories: Mapped[list["Category"]] = relationship(back_populates='user')
    tasks: Mapped[list['Task']] = relationship(back_populates='user')

class Category(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    is_system: Mapped[bool] = mapped_column(default=False)

    # Говорим о том, что у категории есть связь с пользователем и тасками.
    user: Mapped["User"] = relationship(back_populates='categories')
    tasks: Mapped[list['Task']] = relationship(back_populates='category')

class Task(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # Дата ставится бдшкой автоматически.
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'))

    user: Mapped["User"] = relationship(back_populates='tasks')
    category: Mapped["Category"] = relationship(back_populates='tasks')