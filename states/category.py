from aiogram.dispatcher.filters.state import StatesGroup, State


class Category(StatesGroup):
    name = State()


class AddCategory(StatesGroup):
    name = State()


class UpdateCategory(StatesGroup):
    name = State()
    new_name = State()


class DeleteCategory(StatesGroup):
    name = State()
