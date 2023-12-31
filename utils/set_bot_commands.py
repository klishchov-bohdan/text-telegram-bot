from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Start bot'),
        types.BotCommand('help', 'Get help message'),
        types.BotCommand('categories', 'Get category menu'),
        types.BotCommand('files', 'Get file menu'),
    ])
