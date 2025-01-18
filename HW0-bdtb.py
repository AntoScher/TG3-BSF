import os
import asyncio
from dotenv import load_dotenv
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import sqlite3
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()  # изменено 'city' на 'grade'

def init_db():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Загрузка переменных окружения из файла .env
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В каком ты классе?")
    await state.set_state(Form.grade)  # изменено 'city' на 'grade'

@dp.message(Form.grade)  # изменено 'city' на 'grade'
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)  # изменено 'city' на 'grade'
    user_data = await state.get_data()

    try:
        conn = sqlite3.connect('school_data.db')
        cur = conn.cursor()
        cur.execute('''INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
                    (user_data['name'], user_data['age'], user_data['grade']))  # изменено 'city' на 'grade'
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")

    await message.answer("Спасибо за информацию!")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
