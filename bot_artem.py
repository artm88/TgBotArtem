from distutils.ccompiler import get_default_compiler
import time
import logging
import asyncio
import pyowm

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN, WEATHER_TOKEN, MSG

logging.basicConfig(level=logging.INFO)

owm = pyowm.OWM(WEATHER_TOKEN)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    # приветсвенное сообщение
    user_id = message.from_user.id    
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    await message.reply(f"Привет, {user_full_name}!\n Список команд: \
                        \n начало работы /start \n погода /weather \n зеркальный чат /mirror \n напоминание /reminder \n помощь /help \n помощь по зеркальному чату /helpMirror")    
    
@dp.message_handler(commands=['weather'])
async def weather(message: types.Message):
    # погодный модуль
    if message.text.lower() == "/weather":
        await bot.send_message(message.from_user.id, 'Здравствуйте. Вы можете узнать здесь погоду. Напишите название города:')
    else:
        try:
                # Имя города пользователь вводит в чат, после этого мы его передаем в функцию
                observation = owm.weather_at_place(message.text)
                weather = observation.get_weather()
                temp = weather.get_temperature("celsius")["temp"]  # Присваиваем переменной значение температуры из таблицы
                temp = round(temp)
                print(time.ctime(), "User id:", message.from_user.id)
                print(time.ctime(), "Message:", message.text.title(), temp, "C", weather.get_detailed_status())

                # Формируем и выводим ответ
                answer = "В городе " + message.text.title() + " сейчас " + weather.get_detailed_status() + "." + "\n"
                answer += "Температура около: " + str(temp) + " С" + "\n\n"            
        except Exception:
                answer = "Не найден город, попробуйте ввести название снова.\n"
                print(time.ctime(), "User id:", message.from_user.id)
                print(time.ctime(), "Message:", message.text.title(), 'Error')

        await bot.send_message(message.chat.id, answer)  # Ответить сообщением

@dp.message_handler(commands=['mirror'])
# модуль зеркальных ответов
async def process_mirror(message: types.Message):
    await message.reply("Напиши мне что-нибудь!")

@dp.message_handler(commands=["reminder"])
# модуль напоминания пользователю сообщением из файла конфигурации
async def reminder(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    await message.reply("Режим напоминания включен")
    await asyncio.sleep(5)
    await bot.send_message(user_id, MSG.format(user_name))

    for i in range(7):
        await asyncio.sleep(60*60*24)
        await bot.send_message(user_id, MSG.format(user_name))  

@dp.message_handler(commands=['help'])
# список команд
async def process_commands(message: types.Message):
    await message.reply("Список команд: \n начало работы /start \n зеркальный чат /mirror \n напоминание /reminder \n помощь /help \n помощь по зеркальному чату /helpMirror")    

@dp.message_handler(commands=['helpMirror'])
# помощь по модулю зеркальных ответов
async def process_help_mirror(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отправлю этот текст тебе в ответ!")
    

@dp.message_handler()
# модуль ответа бота на сообщение пользователя
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)

