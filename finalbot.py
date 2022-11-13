import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bs4 import BeautifulSoup as b
import random
from telebot import types

URL = 'http://anekdotov.net/anekdot/'
def anek (url):
    r = requests.get(url)
    html = b(r.content, 'html.parser')
    a = html.find_all('div', class_='anekdot')
    return [i.text for i in a]
list_of_a = anek(URL)
random.shuffle(list_of_a)

URL1 = 'https://myfin.by/crypto-rates/bitcoin'
r = requests.get(URL1)
html = b(r.text, 'html.parser')
bit = html.find_all('div', class_="birzha_info_head_rates")
bitcoin = [i.text for i in bit]
coin = (bitcoin[0].strip())
print (coin)



bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/start")
    btn2 = types.KeyboardButton("/anekdot")
    markup.add(btn1, btn2)
    reply_markup = markup
    await message.reply(f'Приветствую, {message.from_user.first_name} {message.from_user.last_name}!\n'
    f'Актуальный курс биткойна: {coin}\n'
    f'Можешь написать название своего города, и я скажу, какая у вас сегодня погодка!\n'
    f'А если хочешь посмеяться с анекдота, введи команду: /anekdot\n'
   )


@dp.message_handler(commands=["anekdot"])
async def anekdot(message: types.Message):
    await message.reply(f'{list_of_a[0]}')
    del list_of_a[0]

@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        await message.reply(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мбар\nВетер: {wind} м/с\n"
              f'Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n'
              f'Продолжительность вашего продуктивного дня: {length_of_the_day}\n'
              f''              
              f"HAVE A GOOD DAY, my little {message.from_user.first_name} {message.from_user.last_name}!"
              )

    except:
        await message.reply("\U00002620 Проверьте название города или команды \U00002620")


if __name__ == '__main__':
    executor.start_polling(dp)
