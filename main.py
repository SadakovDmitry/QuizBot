import time
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from io import BytesIO
from openpyxl import Workbook
from aiogram.types import BufferedInputFile

from utils import make_options_keyboard, start_timer
from config import BOT_TOKEN, ADMIN_IDS
from db import db

# Вопросы квизов (три набора по 10 вопросов каждый)
quiz_sets = [
    # Квиз №1 — Общие знания
    [
        {"question": "Столица Франции?", "options": ["Берлин", "Париж", "Рим", "Лондон"], "answer": 1},
        {"question": "В каком году началась Вторая мировая война?", "options": ["1939", "1914", "1941", "1917"], "answer": 0},
        {"question": "Какое химическое обозначение воды?", "options": ["H2O", "CO2", "O2", "NaCl"], "answer": 0},
        {"question": "Какая планета ближе всего к Солнцу?", "options": ["Земля", "Венера", "Меркурий", "Марс"], "answer": 2},
        {"question": "Автор романа «Война и мир»?", "options": ["Лев Толстой", "Фёдор Достоевский", "Антон Чехов", "Александр Пушкин"], "answer": 0},
        {"question": "Сколько дней в високосном году?", "options": ["366", "365", "364", "367"], "answer": 0},
        {"question": "Какая река самая длинная в мире?", "options": ["Амазонка", "Нил", "Янцзы", "Миссисипи"], "answer": 1},
        {"question": "Какой океан самый большой по площади?", "options": ["Тихий", "Атлантический", "Индийский", "Северный Ледовитый"], "answer": 0},
        {"question": "Химический символ золота?", "options": ["Au", "Ag", "Fe", "Hg"], "answer": 0},
        {"question": "Сколько континентов на Земле?", "options": ["7", "6", "5", "8"], "answer": 0},
    ],

    # Квиз №2 — Культура и наука
    [
        {"question": "Кто автор картины «Мона Лиза»?", "options": ["Леонардо да Винчи", "Микеланджело", "Рафаэль", "Альбрехт Дюрер"], "answer": 0},
        {"question": "Что изучает наука ботаника?", "options": ["Растения", "Животных", "Космос", "Минералы"], "answer": 0},
        {"question": "Какая гора самая высокая на Земле?", "options": ["Эверест", "К2", "Канченджанга", "Лхоцзе"], "answer": 0},
        {"question": "Кто автор серии книг «Гарри Поттер»?", "options": ["Дж. К. Роулинг", "Дж. Р. Р. Толкин", "Джордж Мартин", "Клайв Стейплз Льюис"], "answer": 0},
        {"question": "В какой стране проходили Олимпийские игры 2016 года?", "options": ["Великобритания", "Китай", "Бразилия", "Япония"], "answer": 2},
        {"question": "Что означает аббревиатура CPU в компьютере?", "options": ["Central Processing Unit", "Computer Personal Unit", "Control Processing Unit", "Central Peripheral Unit"], "answer": 0},
        {"question": "Какая валюта используется в Японии?", "options": ["Йена", "Юань", "Вон", "Рупия"], "answer": 0},
        {"question": "Какой цвет в спектре находится между красным и жёлтым?", "options": ["Оранжевый", "Синий", "Фиолетовый", "Зелёный"], "answer": 0},
        {"question": "Какой орган самый большой по массе в человеческом теле?", "options": ["Кожа", "Печень", "Сердце", "Лёгкие"], "answer": 0},
        {"question": "Столица Италии?", "options": ["Рим", "Милан", "Венеция", "Флоренция"], "answer": 0},
    ],

    # Квиз №3 — Россия
    [
        {"question": "Столица России?", "options": ["Москва", "Санкт-Петербург", "Казань", "Новосибирск"], "answer": 0},
        {"question": "Какая река самая длинная в России?", "options": ["Волга", "Лена", "Енисей", "Обь"], "answer": 0},
        {"question": "Какой пик является высочайшим в России?", "options": ["Эльбрус", "Пик Победы", "К2", "Монблан"], "answer": 0},
        {"question": "Кто написал роман «Преступление и наказание»?", "options": ["Фёдор Достоевский", "Лев Толстой", "Антон Чехов", "Николай Гоголь"], "answer": 0},
        {"question": "Какое животное изображено на гербе России?", "options": ["Медведь", "Двуглавый орёл", "Лев", "Тигр"], "answer": 1},
        {"question": "В каком году произошла Октябрьская революция?", "options": ["1917", "1905", "1914", "1920"], "answer": 0},
        {"question": "Сколько республик входит в состав Российской Федерации?", "options": ["22", "21", "23", "24"], "answer": 0},
        {"question": "В каком году была принята современная Конституция РФ?", "options": ["1993", "1991", "2000", "1989"], "answer": 0},
        {"question": "На какой реке стоит Санкт-Петербург?", "options": ["Нева", "Волхов", "Дон", "Ока"], "answer": 0},
        {"question": "Какой символ традиционно ассоциируется с Россией?", "options": ["Матрёшка", "Самовар", "Балалайка", "Кремль"], "answer": 1},
    ],
]


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для регистрации и квиза
class Registration(StatesGroup):
    first_name = State()
    last_name = State()

class QuizState(StatesGroup):
    answering = State()

# Регистрация пользователя
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Registration.first_name)
    await message.answer("👋 Привет! Добро пожаловать в бот для квизов! Введите ваше имя:")

@dp.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Registration.last_name)
    await message.answer("Введите вашу фамилию:")

@dp.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    data = await state.get_data()
    db.register_user(message.from_user.id, data['first_name'], message.text)
    await state.clear()
    await message.answer(f"Регистрация завершена, {data['first_name']} {message.text}!")

# Команда для участников: начать квиз
@dp.message(Command("quiz"))
async def start_quiz_user(message: Message, state: FSMContext):
    # проверяем, есть ли активный квиз и не проходил ли юзер его
    quiz_id = db.get_active_quiz()
    if quiz_id is None:
        return await message.answer("Извините, активных квизов пока нет.")
    if db.has_played(message.from_user.id, quiz_id):
        return await message.answer("Вы уже проходили этот квиз.")
    # фиксируем факт начала (для подсчёта 'начавших')
    db.record_start(message.from_user.id, quiz_id, time.time())
    await state.update_data(
        quiz_id=quiz_id,
        current_idx=0,
        answers=[],
        start_time=time.time(),    # ставим метку старта один раз
    )
    # задаём флаг answered, чтобы таймер сразу заработал
    await state.update_data(answered=False)
    await ask_question(message.chat.id, state)

async def ask_question(chat_id: int, state: FSMContext):
    data = await state.get_data()
    idx = data["current_idx"]
    quiz_id = data["quiz_id"]
    q = quiz_sets[quiz_id-1][idx]

    # строим клавиатуру и сохраняем её в state
    kb = make_options_keyboard(q["options"], idx)
    await state.update_data(
        current_question=q,
        current_keyboard=kb,
        answered=False,
    )

    # отправляем первый текст с 60 секундами
    msg = await bot.send_message(
        chat_id,
        f"❓ Вопрос {idx+1}: {q['question']}\n🕒 Осталось 60 сек",
        reply_markup=kb,
    )

    # стартуем задачу-таймер и сохраняем её, чтобы можно было отменить
    timer_task = asyncio.create_task(
        start_timer(bot, chat_id, msg.message_id, idx, state)
    )
    await state.update_data(timer_task=timer_task)

# Обработка ответов
@dp.callback_query(lambda c: c.data and c.data.startswith("answer_"))
async def answer_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # отменяем таймер
    task = data.get("timer_task")
    if task:
        task.cancel()

    # извлекаем индексы
    _, q_idx, ans_idx = callback.data.split("_")
    q_idx, ans_idx = int(q_idx), int(ans_idx)

    # записываем ответ
    answers = data.get("answers", [])
    answers.append(ans_idx)
    await state.update_data(answers=answers, answered=True)

    # увеличиваем current_idx и проверяем, конец ли квиза
    next_idx = data["current_idx"] + 1
    await state.update_data(current_idx=next_idx)

    total_questions = len(quiz_sets[data["quiz_id"]-1])
    if next_idx < total_questions:
        # следующий вопрос
        await ask_question(callback.from_user.id, state)
    else:
        # считаем результаты
        start = data["start_time"]
        total_time = time.time() - start
        correct = sum(
            1
            for i, user_ans in enumerate(answers)
            if user_ans == quiz_sets[data["quiz_id"]-1][i]["answer"]
        )

        # сохраняем в БД
        db.save_result(callback.from_user.id, data["quiz_id"], correct, total_time)

        # формируем и отсылаем отчёт
        report = (
            f"🎉 Квиз завершён!\n"
            f"✅ Правильных: {correct}/{total_questions}\n"
            f"⏱️ Время: {int(total_time)} сек\n\n"
        )
        for i, user_ans in enumerate(answers):
            q = quiz_sets[data["quiz_id"]-1][i]
            ua = "–" if user_ans is None else q["options"][user_ans]
            ca = q["options"][q["answer"]]
            report += (
                f"{i+1}. {q['question']}\n"
                f"   Ваш ответ: {ua}\n"
                f"   Правильный: {ca}\n\n"
            )
        await bot.send_message(callback.from_user.id, report)

# Команды администратора
@dp.message(Command('start_quiz'))
async def cmd_start_quiz(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.answer("Использование: /start_quiz <номер 1-3>")
    num = int(parts[1])
    if not 1 <= num <= len(quiz_sets):
        return await message.answer("Неверный номер квиза.")
    db.set_active_quiz(num)
    await message.answer(f"Активен квиз №{num}")

@dp.message(Command('stop_quiz'))
async def cmd_stop_quiz(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    db.set_active_quiz(None)
    await message.answer("Квиз остановлен.")

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.answer("Использование: /stats <номер квиза>")
    num = int(parts[1])

    # сколько людей начали и закончили
    started = db.get_started_count(num)
    results = db.get_results(num)  # уже отсортировано correct desc, time asc
    finished = len(results)

    # формируем текст
    text = [
        f"📊 Статистика квиза №{num}:",
        f"👥 Начало: {started}",
        f"✅ Завершили: {finished}",
        "",
        "🏆 Результаты (по правильным ↓, затем времени ↑):"
    ]
    for i, r in enumerate(results, start=1):
        text.append(f"{i}. {r['first_name']} {r['last_name']} — {r['correct_count']} правильных, {int(r['total_time'])} сек")

    await message.answer("\n".join(text))

@dp.message(Command('results'))
async def cmd_results(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.answer("Использование: /results <номер квиза>")
    num = int(parts[1])
    rows = db.get_results(num)
    if not rows:
        return await message.answer("Нет результатов для этого квиза.")
    text = [f"Результаты квиза №{num}:\n"]
    for i, r in enumerate(rows, 1):
        text.append(f"{i}. {r['first_name']} {r['last_name']} — {r['correct_count']} правильных, {r['total_time']} сек")
    await message.answer('\n'.join(text))

@dp.message(Command('export'))
async def cmd_export(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.answer("Использование: /export <номер квиза>")

    num = int(parts[1])
    rows = db.get_results(num)

    # Собираем Excel в памяти
    wb = Workbook()
    ws = wb.active
    ws.append(["Имя", "Фамилия", "Правильных", "Время (сек)"])
    for r in rows:
        ws.append([r['first_name'], r['last_name'], r['correct_count'], r['total_time']])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # Готовим и отправляем файл из буфера
    data = buffer.getvalue()
    filename = f"results_quiz{num}.xlsx"
    doc = BufferedInputFile(data, filename=filename)
    await message.answer_document(document=doc, caption=f"Результаты квиза №{num}")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
