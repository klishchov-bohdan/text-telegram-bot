from filters import IsPrivate, IsAdmin
from keyboards.inline import admin_files_edit_menu as afem
from keyboards.inline import file_edit_menu as fem
from states import AddFile, SendFiles, EditFile
from utils.db_api import category_commands, file_commands
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from keyboards.inline.text_file import admin_files_menu as afm_kb
from keyboards.inline import sorting_edit_files_menu as sefm
from keyboards.inline.text_file import file_edit_delete_cancel as fedc
from keyboards.inline.text_file import cancel_add_file as caf
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import aiofiles.os

from data import config
from loader import dp, bot


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), Command('files'))
async def command_categories(message: types.Message):
    await message.answer('Выберите действие с файлами: ', reply_markup=afm_kb)


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='add_file')
async def new_file(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.edit_text('Выберите действие с файлами: Добавить файл')
    count_categories = await category_commands.count_categories()
    if count_categories == 0:
        await call.message.answer('Сначала добавьте хотя бы одну категорию')
    else:
        msg = await call.message.answer('Введите название нового файла:', reply_markup=caf)
        s = dp.current_state(user=call.from_user.id)
        await s.update_data(msg_id=msg.message_id)
        await AddFile.name.set()


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='cancel_add_file', state=AddFile.states)
async def cancel_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Добавление файла отменено')


@rate_limit(limit=3)
@dp.message_handler(state=AddFile.name, content_types=types.ContentType.TEXT)
async def set_file_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_initiator = data.get('msg_id')
    await bot.edit_message_reply_markup(chat_id=message.chat.id,
                                        message_id=msg_initiator,
                                        reply_markup=InlineKeyboardMarkup())
    answer = message.text
    await state.update_data(name=answer)
    msg = await message.answer(f'Введите описание файла:', reply_markup=caf)
    s = dp.current_state(user=message.from_user.id)
    await s.update_data(msg_id=msg.message_id)
    await AddFile.description.set()


@rate_limit(limit=3)
@dp.message_handler(state=AddFile.description, content_types=types.ContentType.TEXT)
async def set_file_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_initiator = data.get('msg_id')
    await bot.edit_message_reply_markup(chat_id=message.chat.id,
                                        message_id=msg_initiator,
                                        reply_markup=InlineKeyboardMarkup())
    answer = message.text
    await state.update_data(description=answer)
    categories = await category_commands.get_all_categories()
    inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                              one_time_keyboard=True, inline_keyboard=[])
    for category in categories:
        inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                        callback_data=f'{category.category_name}')])
    inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text='Отменить',
                                                                    callback_data='cancel_add_file')])
    await message.answer("Выберите категорию:", reply_markup=inline_category_kb)
    await AddFile.category.set()


@rate_limit(limit=3)
@dp.callback_query_handler(state=AddFile.category)
async def get_file_category(call: CallbackQuery, state: FSMContext):
    try:
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            await call.message.edit_reply_markup()
            answer = call.data
            await call.message.edit_text(f'Выберите категорию: {answer}')
            await state.update_data(category=answer)
            await call.message.answer('Отправьте файл с расширением .docx для сохранения:', reply_markup=caf)
            await AddFile.path.set()
        else:
            await call.message.answer('Вы должны выбрать категорию')
    except Exception as ex:
        print(ex)
        await call.message.answer("Что-то пошло не так при определении категории файла")
        await state.finish()


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), state=AddFile.path, content_types=types.ContentType.DOCUMENT)
async def get_text_file(message: types.Message, state: FSMContext):
    try:
        if message.document.file_name.split('.')[-1] == 'docx':
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            data = await state.get_data()
            file_category = data.get('category')
            file_name = data.get('name')
            file_description = data.get('description')
            await bot.download_file(file_path, f'files/{file_id}.docx')
            await file_commands.add_file(file_id, file_name, file_category, file_description)
            await message.answer('Файл успешно сохранен')
            await state.finish()
        else:
            await message.answer('Файл должен быть расширения .docx')
    except Exception as ex:
        print(ex)
        await message.answer("Что-то пошло не так при отправке файла")
        await state.finish()


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='edit_files')
async def edit_files(call: types.CallbackQuery):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите действие с файлами: Изменить/удалить файлы')
        files_count = await file_commands.count_files()
        if files_count != 0:
            files = await file_commands.get_all_files()
            await call.message.answer_document(document=files[0].file_id,
                                               caption=f'Имя файла: {files[0].file_name}\n\n'
                                                       f'Категория: {files[0].file_category}\n\n'
                                                       f'Описание: {files[0].file_description}',
                                               reply_markup=afem)
            await SendFiles.files.set()
            await SendFiles.current_idx.set()
            s = dp.current_state(user=call.from_user.id)
            await s.update_data(files=files)
            await s.update_data(current_idx=0)
        else:
            await call.message.answer('Никаких файлов пока не добавлено')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении файлов')


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_cancel_edit_files_menu', state=SendFiles.states)
async def cancel_categories_menu(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Отменено')


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_send_prev_file', state=SendFiles.states)
async def admin_send_prev_file(call: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        files = data.get('files')
        current_idx = data.get('current_idx')
        if current_idx != 0:
            await call.message.delete()
            await call.message.answer_document(document=files[current_idx - 1].file_id,
                                               caption=f'Имя файла: {files[current_idx - 1].file_name}\n\n'
                                                       f'Категория: {files[current_idx - 1].file_category}\n\n'
                                                       f'Описание: {files[current_idx - 1].file_description}',
                                               reply_markup=afem)
            await state.update_data(current_idx=current_idx - 1)
        else:
            await call.answer('Это первый файл в списке')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_send_next_file', state=SendFiles.states)
async def admin_send_next_file(call: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        files = data.get('files')
        current_idx = data.get('current_idx')
        if current_idx != len(files) - 1:
            await call.message.delete()
            await call.message.answer_document(document=files[current_idx + 1].file_id,
                                               caption=f'Имя файла: {files[current_idx + 1].file_name}\n\n'
                                                       f'Категория: {files[current_idx + 1].file_category}\n\n'
                                                       f'Описание: {files[current_idx + 1].file_description}',
                                               reply_markup=afem)
            await state.update_data(current_idx=current_idx + 1)
        else:
            await call.answer('Это последний файл в списке')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_selected_file', state=SendFiles.states)
async def edit_file(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        data = await state.get_data()
        files = data.get('files')
        current_idx = data.get('current_idx')
        await state.finish()
        await EditFile.file_id.set()
        s = dp.current_state(user=call.from_user.id)
        await s.update_data(file_id=files[current_idx].file_id)
        await call.message.answer('Выберите поле, которое хотите редактировать',
                                  reply_markup=fem)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_cancel_edit_file', state=EditFile.file_id)
async def cancel_admin_edit_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Редактирование отменено')


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_delete_file_cancel',
                           state=[EditFile.name, EditFile.description, EditFile.document, SendFiles.files, SendFiles.current_idx])
async def file_edit_delete_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.finish()
    await call.message.answer('Действие отменено')


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_file_name', state=EditFile.file_id)
async def admin_edit_file_name(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.message.answer('Введите новое имя файла:', reply_markup=fedc)
        await EditFile.name.set()
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), IsAdmin(), state=EditFile.name)
async def admin_get_new_file_name(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        file_id = data.get('file_id')
        await file_commands.update_file_name(file_id, message.text)
        await message.answer('Имя файла успешно изменено')
        await state.finish()
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_file_description', state=EditFile.file_id)
async def admin_edit_file_description(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.message.answer('Введите новое описание файла:', reply_markup=fedc)
        await EditFile.description.set()
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), IsAdmin(), state=EditFile.description)
async def admin_get_new_file_description(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        file_id = data.get('file_id')
        await file_commands.update_file_description(file_id, message.text)
        await message.answer('Описание файла успешно изменено')
        await state.finish()
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_file_category', state=EditFile.file_id)
async def admin_edit_file_category(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        categories = await category_commands.get_all_categories()
        data = await state.get_data()
        file_id = data.get('file_id')
        file_db = await file_commands.get_file(file_id)
        categories = list(filter(lambda x: x.category_name != file_db.file_category, categories))
        if len(categories) >= 1:
            inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                      one_time_keyboard=True, inline_keyboard=[])
            for category in categories:
                inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                                callback_data=f'{category.category_name}')])
            inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text='Отменить',
                                                                            callback_data='admin_cancel_edit_category')])
            await call.message.answer('Выберите новую категорию файла:', reply_markup=inline_category_kb)
            await EditFile.category.set()
        else:
            await call.message.answer('Для изменении категории файла создайте еще хотя бы одну категорию')
            await state.finish()
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_cancel_edit_category', state=EditFile.category)
async def cancel_admin_edit_category(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Редактирование отменено')


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), state=EditFile.category)
async def admin_get_file_category(call: CallbackQuery, state: FSMContext):
    try:
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            await call.message.edit_reply_markup()
            answer = call.data
            data = await state.get_data()
            file_id = data.get('file_id')
            await file_commands.update_file_category(file_id, answer)
            await call.message.answer('Категория успешно изменена')
            await state.finish()
        else:
            await call.message.answer('Вы должны выбрать категорию')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_edit_file_document', state=EditFile.file_id)
async def admin_edit_file_document(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.message.answer('Отправьте новый документ в формате .docx:', reply_markup=fedc)
        await EditFile.document.set()
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.message_handler(IsPrivate(), IsAdmin(), state=EditFile.document, content_types=types.ContentType.DOCUMENT)
async def admin_get_new_file_document(message: types.Message, state: FSMContext):
    try:
        if message.document.file_name.split('.')[-1] == 'docx':
            new_file_id = message.document.file_id
            file = await bot.get_file(new_file_id)
            file_path = file.file_path
            data = await state.get_data()
            file_id = data.get('file_id')
            await aiofiles.os.remove(f'files/{file_id}.docx')
            await bot.download_file(file_path, f'files/{new_file_id}.docx')
            await file_commands.update_file_id(file_id, new_file_id)
            await message.answer('Файл успешно изменен')
            await state.finish()
        else:
            await message.answer('Файл должен быть расширения .docx')
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так при редактировании файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_delete_selected_file', state=SendFiles.states)
async def edit_file(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    files = data.get('files')
    current_idx = data.get('current_idx')
    file_delete_confirmation = InlineKeyboardMarkup(row_width=2,
                                                    resize_keyboard=True,
                                                    one_time_keyboard=True,
                                                    inline_keyboard=[
                                                        [
                                                            InlineKeyboardButton(text='Удалить',
                                                                                 callback_data='admin_delete_confirmation'),
                                                        ],
                                                        [
                                                            InlineKeyboardButton(text='Отменить',
                                                                                 callback_data='admin_edit_delete_file_cancel'),
                                                        ],
                                                    ])
    await call.message.answer(f'Вы уверены что хотите удалить данный файл? [{files[current_idx].file_name}]', reply_markup=file_delete_confirmation)


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='admin_delete_confirmation', state=SendFiles.states)
async def edit_file(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        data = await state.get_data()
        files = data.get('files')
        current_idx = data.get('current_idx')
        await state.finish()
        await aiofiles.os.remove(f'files/{files[current_idx].file_id}.docx')
        await file_commands.delete_file(files[current_idx].file_id)
        await call.message.answer('Файл успешно удален')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при удалении файла')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='send_sorted_documents_edit', state=SendFiles.states)
async def sort_files(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.message.answer('Выберите тип сортировки',
                                  reply_markup=sefm)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='alphabetically_sorting_edit', state=SendFiles.states)
async def sort_alphabetically(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите тип сортировки: Сортировка от А до Я')
        data = await state.get_data()
        files = data.get('files')
        files.sort(key=lambda file: file.file_name.lower())
        await state.update_data(files=files)
        await state.update_data(files=files)
        await call.message.answer_document(document=files[0].file_id,
                                           caption=f'Имя файла: {files[0].file_name}\n\n'
                                                   f'Категория: {files[0].file_category}\n\n'
                                                   f'Описание: {files[0].file_description}',
                                           reply_markup=afem)
        await state.update_data(current_idx=0)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(IsAdmin(), text='alphabetically_sorting_reverse_edit', state=SendFiles.states)
async def sort_alphabetically_reverse(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите тип сортировки: Сортировка от Я до А')
        data = await state.get_data()
        files = data.get('files')
        files.sort(reverse=True, key=lambda file: file.file_name.lower())
        await state.update_data(files=files)
        await state.update_data(files=files)
        await call.message.answer_document(document=files[0].file_id,
                                           caption=f'Имя файла: {files[0].file_name}\n\n'
                                                   f'Категория: {files[0].file_category}\n\n'
                                                   f'Описание: {files[0].file_description}',
                                           reply_markup=afem)
        await state.update_data(current_idx=0)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()
