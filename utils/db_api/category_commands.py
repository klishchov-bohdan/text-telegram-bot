from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.category import Category


async def add_category(category_name: str):
    try:
        category = Category(category_name=category_name)
        await category.create()
    except UniqueViolationError:
        print('Category cant be created')


async def get_all_categories():
    files = await Category.query.gino.all()
    return files


async def count_categories():
    count = await db.func.count(Category.category_name).gino.scalar()
    return count


async def delete_category(category_name: str):
    category = await Category.get(category_name)
    await category.delete()


async def update_category_name(category_name: str, new_category_name: str):
    category = await Category.query.where(Category.category_name == category_name).gino.first()
    await category.update(category_name=new_category_name).apply()
