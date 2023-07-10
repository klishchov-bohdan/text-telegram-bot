from aiogram.dispatcher.filters.state import StatesGroup, State


class File(StatesGroup):
    path = State()
    name = State()
    category = State()
    description = State()


class AddFile(StatesGroup):
    path = State()
    name = State()
    category = State()
    description = State()
    msg_id = State()


class SendFiles(StatesGroup):
    files = State()
    category = State()
    current_idx = State()
    msg_id = State()


class EditFile(StatesGroup):
    file_id = State()
    name = State()
    category = State()
    description = State()
    document = State()
