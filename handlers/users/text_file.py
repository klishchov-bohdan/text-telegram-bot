import asyncio
import io

from filters import IsPrivate, IsAdmin
from keyboards.inline import file_send_menu as fsm, sorting_files_menu
from states import SendFiles, Category
from utils.db_api import category_commands, file_commands
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from keyboards.inline.text_file import files_menu as fm_kb
from keyboards.inline.text_file import cancel_add_file as caf
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile, InputMedia, \
    InputMediaDocument
from aiogram.utils.exceptions import BadRequest

from data import config
from loader import dp, bot


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), Command('files'))
async def command_categories(message: types.Message):
    await message.answer('Выберите действие с файлами: ', reply_markup=fm_kb)


@dp.callback_query_handler(text='cancel_files_menu')
async def cancel_categories_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('Отменено')


@rate_limit(limit=3)
@dp.callback_query_handler(text='all_files')
async def all_files(call: types.CallbackQuery):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите действие с файлами: Все файлы')
        files_count = await file_commands.count_files()
        if files_count != 0:
            files = await file_commands.get_all_files()
            await call.message.answer_document(document=files[0].file_id,
                                               caption=f'Имя файла: {files[0].file_name}\n\n'
                                                       f'Категория: {files[0].file_category}\n\n'
                                                       f'Описание: {files[0].file_description}',
                                               reply_markup=fsm)
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


@rate_limit(limit=3)
@dp.callback_query_handler(text='files_by_category')
async def files_by_category(call: types.CallbackQuery):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите действие с файлами: Файлы по категориям')
        categories = await category_commands.get_all_categories()
        inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                  one_time_keyboard=True, inline_keyboard=[])
        for category in categories:
            inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                            callback_data=f'{category.category_name}')])
        await call.message.answer('Выберите одну из категорий для получения списка имеющихся текстов',
                                  reply_markup=inline_category_kb)
        await SendFiles.category.set()
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении категорий')


@dp.callback_query_handler(state=SendFiles.category)
async def get_category(call: CallbackQuery, state: FSMContext):
    try:
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            await call.message.edit_reply_markup()
            await call.message.edit_text(f'Выберите одну из категорий для получения списка имеющихся текстов: {call.data}')
            answer = call.data
            files = await file_commands.get_files_by_category(answer)
            if len(files) > 0:
                await call.message.answer_document(document=files[0].file_id,
                                                   caption=f'Имя файла: {files[0].file_name}\n\n'
                                                           f'Категория: {files[0].file_category}\n\n'
                                                           f'Описание: {files[0].file_description}',
                                                   reply_markup=fsm)
                await state.finish()
                await SendFiles.files.set()
                await SendFiles.current_idx.set()
                s = dp.current_state(user=call.from_user.id)
                await s.update_data(files=files)
                await s.update_data(current_idx=0)
            else:
                await call.message.answer('Файлов в данной категории пока не существует')
                await state.finish()
        else:
            await call.message.answer('Вы должны выбрать категорию')
    except Exception as ex:
        await call.message.answer('Что-то пошло не так')
        print(ex)
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(text='cancel_send_files', state=SendFiles.states)
async def cancel_send_files(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Просмотр файлов отменен')


@rate_limit(limit=1)
@dp.callback_query_handler(text='send_prev_file', state=SendFiles.states)
async def send_prev_file(call: types.CallbackQuery, state: FSMContext):
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
                                               reply_markup=fsm)
            await state.update_data(current_idx=current_idx - 1)
        else:
            await call.answer('Это первый файл в списке')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(text='send_next_file', state=SendFiles.states)
async def send_next_file(call: types.CallbackQuery, state: FSMContext):
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
                                               reply_markup=fsm)
            await state.update_data(current_idx=current_idx + 1)
        else:
            await call.answer('Это последний файл в списке')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при получении файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(text='send_sorted_documents', state=SendFiles.states)
async def sort_files(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        await call.message.answer('Выберите тип сортировки',
                                  reply_markup=sorting_files_menu)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(text='alphabetically_sorting', state=SendFiles.states)
async def sort_alphabetically(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите тип сортировки: Сортировка от А до Я')
        data = await state.get_data()
        files = data.get('files')
        files.sort(key=lambda file: file.file_name.lower())
        await state.update_data(files=files)
        await call.message.answer_document(document=files[0].file_id,
                                           caption=f'Имя файла: {files[0].file_name}\n\n'
                                                   f'Категория: {files[0].file_category}\n\n'
                                                   f'Описание: {files[0].file_description}',
                                           reply_markup=fsm)
        await state.update_data(current_idx=0)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()


@rate_limit(limit=1)
@dp.callback_query_handler(text='alphabetically_sorting_reverse', state=SendFiles.states)
async def sort_alphabetically_reverse(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_reply_markup()
        await call.message.edit_text('Выберите тип сортировки: Сортировка от Я до А')
        data = await state.get_data()
        files = data.get('files')
        files.sort(reverse=True, key=lambda file: file.file_name.lower())
        await state.update_data(files=files)
        await call.message.answer_document(document=files[0].file_id,
                                           caption=f'Имя файла: {files[0].file_name}\n\n'
                                                   f'Категория: {files[0].file_category}\n\n'
                                                   f'Описание: {files[0].file_description}',
                                           reply_markup=fsm)
        await state.update_data(current_idx=0)
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при сортировке файлов')
        await state.finish()


# @rate_limit(limit=1)
# @dp.callback_query_handler(text='searching_text', state=SendFiles.states)
# async def search_files(call: types.CallbackQuery, state: FSMContext):
#     try:
#         await call.message.delete()
#         msg = await call.message.answer('Введите название текста, который хотите найти:',
#                                         reply_markup=cancel_searching_text)
#         await state.update_data(msg_id=msg.message_id)
#         await SendFiles.search.set()
#     except Exception as ex:
#         print(ex)
#         await call.message.answer('Что-то пошло не так при поиске файлов')
#         await state.finish()
#
#
# @rate_limit(limit=1)
# @dp.callback_query_handler(text='cancel_searching', state=SendFiles.search)
# async def cancel_searching(call: types.CallbackQuery, state: FSMContext):
#     try:
#         await call.message.delete()
#         await state.update_data(search=None)
#         await call.message.answer('Поиск файлов отменен')
#         files_count = await file_commands.count_files()
#         if files_count != 0:
#             files = await file_commands.get_all_files()
#             await call.message.answer_document(document=files[0].file_id,
#                                                caption=f'Имя файла: {files[0].file_name}\n\n'
#                                                        f'Категория: {files[0].file_category}\n\n'
#                                                        f'Описание: {files[0].file_description}',
#                                                reply_markup=fsm)
#             await state.update_data(files=files)
#             await state.update_data(current_idx=0)
#         else:
#             await call.message.answer('Никаких файлов пока не добавлено')
#
#     except Exception as ex:
#         print(ex)
#         await call.message.answer('Что-то пошло не так при получении файлов')
#
#
# @rate_limit(limit=1)
# @dp.message_handler(IsPrivate(), state=SendFiles.search, content_types=types.ContentType.TEXT)
# async def searching_files(message: types.Message, state: FSMContext):
#     try:
#         data = await state.get_data()
#         msg_initiator = data.get('msg_id')
#         await bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                             message_id=msg_initiator,
#                                             reply_markup=InlineKeyboardMarkup())
#         await bot.edit_message_text(text=f'Введите название текста, который хотите найти: {message.text}',
#                                     chat_id=message.chat.id,
#                                     message_id=msg_initiator)
#         files = data.get('files')
#         filter_files = filter(lambda file: message.text in file.file_name, files)
#         if len(list(filter_files)) > 0:
#             await state.update_data(files=list(filter_files))
#             await message.answer_document(document=files[0].file_id,
#                                           caption=f'Имя файла: {files[0].file_name}\n\n'
#                                                   f'Категория: {files[0].file_category}\n\n'
#                                                   f'Описание: {files[0].file_description}',
#                                           reply_markup=fsm)
#             await state.update_data(current_idx=0)
#         else:
#             await message.answer(f'Файлов по запросу [{message.text}] не найдено',
#                                  reply_markup=cancel_searching_text)
#     except Exception as ex:
#         print(ex)
#         await message.answer('Что-то пошло не так при получении файлов')

