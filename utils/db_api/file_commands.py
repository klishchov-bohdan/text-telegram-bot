from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.file import File


async def add_file(file_id: str, file_name: str, file_category: str, file_description: str):
    try:
        file = File(file_id=file_id, file_name=file_name, file_category=file_category, file_description=file_description)
        await file.create()
    except UniqueViolationError:
        print('File cant be created')


async def get_all_files():
    files = await File.query.gino.all()
    return files


async def count_files():
    count = await db.func.count(File.file_id).gino.scalar()
    return count


async def get_file(file_id: str):
    file = await File.query.where(File.file_id == file_id).gino.first()
    return file


async def get_files_by_category(category: str):
    files = await File.query.where(File.file_category == category).gino.all()
    return files


async def update_file_name(file_id: str, new_name: str):
    file = await File.query.where(File.file_id == file_id).gino.first()
    await file.update(file_name=new_name).apply()


async def update_file_description(file_id: str, new_description: str):
    file = await File.query.where(File.file_id == file_id).gino.first()
    await file.update(file_description=new_description).apply()


async def update_file_category(file_id: str, new_category: str):
    file = await File.query.where(File.file_id == file_id).gino.first()
    await file.update(file_category=new_category).apply()


async def update_file_id(file_id: str, new_file_id: str):
    file = await File.query.where(File.file_id == file_id).gino.first()
    await file.update(file_id=new_file_id).apply()


async def update_files_category(old_category: str, new_category: str):
    files = await File.query.where(File.file_category == old_category).gino.all()
    for file in files:
        await file.update(file_category=new_category).apply()


async def delete_file(file_id: str):
    file = await File.get(file_id)
    await file.delete()
