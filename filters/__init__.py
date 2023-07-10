from aiogram import Dispatcher

from .is_admin import IsAdmin
from .private_chat import IsPrivate


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsAdmin)
    