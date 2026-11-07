from .db import async_session
from .models import User, Category, Task
from sqlalchemy import select, update, delete

# =======================================
# ГРУППА ФУНКЦИЙ ДЛЯ USER
# =======================================

"""Создаём нового пользователя"""
async def add_user(telegram_id, username):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        # Возвращает 1 объект или None.
        user = result.scalar_one_or_none()

        if user is not None:
            return user

        user = User(telegram_id=telegram_id, user_name=username)
        session.add(user)
        await session.flush() # отправляет изменения в БД, но пока не фиксирует их.

        category = Category(user_id=user.id, name='Общие', is_system=True)
        session.add(category)
        await session.commit()

        return user
    
"""Получаем пользователя"""
async def get_user(telegram_id):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        return user

# =======================================
# ГРУППА ФУНКЦИЙ ДЛЯ CATEGORY
# =======================================

"""Добавляем категорию задач"""
async def add_category(user_id, name):
    async with async_session() as session:
        category = Category(user_id=user_id, name=name)
        session.add(category)
        await session.commit()

        return category
    
"""Получаем ВСЕ категории пользователя"""
async def get_all_categories(user_id):
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.user_id == user_id)
        )
        categories = result.scalars().all()
        return categories

"""Получаем какую-то одну категорию пользователя"""
async def get_category(category_id):
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        return category

"""Удаляем категорию по его id"""
async def delete_category(category_id):
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )

        category = result.scalar_one_or_none()

        if category is not None:
            await session.delete(category)
            await session.commit()

"""Меняем название категории"""
async def update_category_name(category_id, new_name):
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )

        category = result.scalar_one_or_none()

        if category is not None:
            category.name = new_name
            await session.commit()
        return category


# =======================================
# ГРУППА ФУНКЦИЙ ДЛЯ TASK
# =======================================
"""Создаём новую задачу"""
async def add_task(user_id, category_id, title):
    async with async_session() as session:
        task = Task(user_id=user_id, category_id=category_id, title=title)
        session.add(task)
        await session.commit()
        return task

"""Возвращаем список задач в одной конкретной категории"""
async def get_tasks_by_category(category_id, user_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(
                (Task.category_id == category_id) & 
                (Task.user_id == user_id) &
                (Task.is_done == False)
                )
        )
        tasks_by_category = result.scalars().all()
        return tasks_by_category

"""Возвращаем ВСЕ задачи из всех групп"""
async def get_all_tasks(user_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where((Task.user_id == user_id) & (Task.is_done == False))
        )
        all_tasks = result.scalars().all()
        return all_tasks

"""Возвращаем одну задачу по id"""
async def get_task(task_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        one_task = result.scalar_one_or_none()
        return one_task

"""Отмечаем задачу выполненной"""
async def mark_task_done(task_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        marking_task = result.scalar_one_or_none()
        if marking_task is not None:
            marking_task.is_done = True
            await session.commit()
        return marking_task

"""Удаляем задачу"""
async def delete_task(task_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is not None:
            await session.delete(task)
            await session.commit()

"""Редактировать задачу"""
async def update_task_title(task_id, new_title):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        update_task = result.scalar_one_or_none()
        if update_task is not None:
            update_task.title = new_title
            await session.commit()
        return update_task

"""Получение списка выполненных задач"""
async def get_done_tasks(user_id):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where((Task.user_id == user_id) & (Task.is_done == True))
        )
        done_tasks = result.scalars().all()
        return done_tasks

