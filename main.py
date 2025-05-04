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
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils import make_options_keyboard, start_timer
from config import BOT_TOKEN, ADMIN_IDS
from db import db

quiz_names = [
    "Внеучебная деятельность в МФТИ",
    "Кем становятся выпускники?",
    "Как поступить на Физтех?",
]

# Вопросы квизов (три набора по 10 вопросов каждый)
quiz_sets = [
    # Квиз №1 — Внеучебка
    [
        {"question": "Какие крупные внеучебные мероприятия проводятся в МФТИ?", "options": ["Спартакиада", "Матч века", "День Физика", "Все перечисленные"], "answer": 3},
        {"question": "Сколько дней обычно длятся Дни Физтеха?", "options": ["1", "2", "3", "4"], "answer": 3},
        {"question": "Какое мероприятие традиционно завершает Дни Физтеха?", "options": ["Дискотека", "Музыкальный концерт", "Турнир", "Пенная вечеринка"], "answer": 1import time
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from io import BytesIO
from openpyxl import Workbook
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils import make_options_keyboard, start_timer
from config import BOT_TOKEN, ADMIN_IDS
from db import db

quiz_names = [
    "Внеучебная деятельность в МФТИ",
    "Кем становятся выпускники?",
    "Как поступить на Физтех?",
]

# Вопросы квизов (три набора по 10 вопросов каждый)
quiz_sets = [
    # Квиз №1 — Внеучебка
    [
        {"question": "Какие крупные внеучебные мероприятия проводятся в МФТИ?", "options": ["Спартакиада", "Матч века", "День Физика", "Все перечисленные"], "answer": 3},
        {"question": "Сколько дней обычно длятся Дни Физтеха?", "options": ["1", "2", "3", "4"], "answer": 3},
        {"question": "Какое мероприятие традиционно завершает Дни Физтеха?", "options": ["Дискотека", "Музыкальный концерт", "Турнир", "Пенная вечеринка"], "answer": 1},
        {"question": "Когда проводится День первокурсника в МФТИ?", "options": ["30 августа", "31 августа", "1 сентября", "2 сентября"], "answer": 2},
        {"question": "Что такое Матч века в МФТИ?", "options": ["Непрерывный 24-часовой матч", "Матч победителей турнира", "Встреча выпускников", "Обычный матч между командами"], "answer": 0},
        {"question": "Кто может участвовать в организации мероприятий в МФТИ?", "options": ["Любой желающий студент", "Только студенты старше второго курса", "Только с опытом организации", "Только сотрудники МФТИ"], "answer": 0},
        {"question": "Сколько человек максимум собиралось на День рождения факультета в МФТИ?", "options": ["Около 2500", "Около 2000", "Около 1500", "Около 1000"], "answer": 0},
        {"question": "Какой из праздников не отмечается в МФТИ?", "options": ["23 февраля", "Хэллоуин", "1 апреля", "8 марта"], "answer": 1},
        {"question": "Какая конференция МФТИ включает секции по бизнесу и технологическому предпринимательству?", "options": ["Всероссийская научная конференция", "Startup Village", "Форум «Территория»", "Технопарк"], "answer": 0},
        {"question": "Какое мероприятие помогает студентам наладить контакт с научными центрами и потенциальными работодателями?", "options": ["Карьерный форсаж", "Startup Village", "Олимпиада «Физтех»", "Научная конференция"], "answer": 0},
        {"question": "Какая возможность есть у студентов МФТИ для международного опыта?", "options": ["Стажировки в зарубежных вузах", "Участие в научных конференциях", "Карьерный форсаж", "Физтех-Фест"], "answer": 0},
    ],

    # Квиз №2 - Кем становятся выпускники
    [
        {"question": "Какой процент выпускников МФТИ остаются и работают в России после окончания обучения?", "options": ["75–80%", "80–85%", "94–95%", "100%"], "answer": 2},
        {"question": "Средняя зарплата выпускников МФТИ, работающих в Москве, составляет примерно:", "options": ["200 000 ₽", "235 000 ₽", "270 000 ₽", "300 000 ₽"], "answer": 2},
        {"question": "Какое направление является наиболее востребованным у выпускников МФТИ согласно данным «Вузопедия»?", "options": ["Разработка ПО и информационная безопасность", "Химическая промышленность", "Финансовый анализ", "Архитектура и дизайн"], "answer": 0},
        {"question": "В каких ролях чаще всего начинают работать выпускники МФТИ?", "options": ["Инженер, программист, конструктор", "Юрист, экономист, менеджер", "Врач, учитель, журналист", "Маркетолог, дизайнер, HR"], "answer": 0},
        {"question": "Сколько академиков и членов-корреспондентов РАН выпустил МФТИ?", "options": ["Около 50", "Около 150", "Около 300", "Более 500"], "answer": 3},
        {"question": "Сколько лауреатов Нобелевской премии среди выпускников МФТИ?", "options": ["1", "2", "3", "4"], "answer": 2},
        {"question": "Сколько космонавтов-героев Советского Союза и России окончили МФТИ?", "options": ["1", "2", "3", "4"], "answer": 3},
        {"question": "Где студенты МФТИ могут проходить стажировку по направлению «Когнитивные технологии»?", "options": ["Google", "Cognitive Technologies", "Yandex", "IBM"], "answer": 1},
        {"question": "Какая позиция МФТИ в рейтинге вузов по уровню зарплат IT-специалистов в Москве?", "options": ["Первая", "Вторая", "Третья", "Четвёртая"], "answer": 0},
        {"question": "Из каких профессий часто приходят предложения о работе студентам МФТИ ещё во время учёбы?", "options": ["Аналитик данных и статистик", "Водитель и курьер", "Продавец и кассир", "Художник и скульптор"], "answer": 0},
    ],

    # Квиз №3 — Довуз
    [
        {"question": "Какая олимпиада даёт льготы при поступлении в МФТИ?", "options": ["Всероссийская олимпиада школьников", "«Физтех» (проводится МФТИ)", "«Курчатов»", "Все перечисленные"], "answer": 3},
        {"question": "Что такое ЗФТШ?", "options": ["Заочная физико-техническая школа при МФТИ", "Зимняя физико-техническая смена", "Программа для магистров", "Спортивный клуб МФТИ"], "answer": 0},
        {"question": "Какое минимальное количество баллов ЕГЭ по математике требуется для подачи документов в 2025 году?", "options": ["50", "70", "85", "Минимум не установлен, важна конкуренция"], "answer": 2},
        {"question": "Как называется дополнительное вступительное испытание (ДВИ) в МФТИ?", "options": ["Собеседование по физике", "Экзамен по математике и физике", "Тест на IQ", "ДВИ отсутствует, учитываются только ЕГЭ и олимпиады"], "answer": 3},
        {"question": "Какие программы помогают подготовиться к поступлению?", "options": ["Школы МФТИ", "Онлайн-курсы на Stepik", "ЗФТШ", "Все перечисленные"], "answer": 3},
        {"question": "Сколько этапов включает олимпиада «Физтех»?", "options": ["1 (только заключительный)", "2 (отборочный и заключительный)", "3 (школьный, муниципальный, всероссийский)", "Олимпиада не проводится"], "answer": 1},
        {"question": "Что учитывается в портфолио абитуриента?", "options": ["Спортивные достижения", "Участие в научных конференциях", "Аттестат с отличием", "Только баллы ЕГЭ"], "answer": 2},
        {"question": "Когда проходит «День открытых дверей» в МФТИ?", "options": ["Только зимой", "Весной и осенью", "Летом перед подачей документов", "Не проводится"], "answer": 1},
        {"question": "Какое преимущество дает победа в олимпиаде «Физтех»?", "options": ["Зачисление без экзаменов", "100 баллов по профильному предмету", "Дополнительные баллы к ЕГЭ", "Все перечисленные варианты"], "answer": 0},
        {"question": "Сколько абитуриентов поступило по БВИ в 2024 году?", "options": ["Больше 75%", "Меньше 50% но больше 25%", "Больше 50% но меньше 75%", "Меньше 25%"], "answer": 2},
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
    # 1) если не зарегистрирован — запускаем FSM на ввод ФИО
    if not db.is_registered(message.from_user.id):
        await state.set_state(Registration.first_name)
        return await message.answer(
            "👋 Привет! Добро пожаловать в бот для квизов! Введите ваше имя:"
        )

    # 2) иначе — показываем статус активного квиза и кнопку «Начать квиз»
    quiz_id = db.get_active_quiz()
    kb = ReplyKeyboardBuilder()
    kb.button(text="Начать квиз")
    kb.adjust(1)
    markup = kb.as_markup(resize_keyboard=True)

    if quiz_id is None:
        text = (
            "Когда администратор запустит квиз, вы получите уведомление с кнопкой для участия.\n"
            "Удачи! 🍀"
        )
    else:
        name = quiz_names[quiz_id - 1]
        text = f"Сейчас активен квиз «{name}». Вы можете присоединиться к нему."

    await message.answer(text, reply_markup=markup)



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
    quiz_id = db.get_active_quiz()
    kb = ReplyKeyboardBuilder()
    kb.button(text="Начать квиз")
    kb.adjust(1)
    markup = kb.as_markup(resize_keyboard=True)

    if quiz_id is None:
        text = (
            "Когда администратор запустит квиз, вы получите уведомление с кнопкой для участия.\n"
            "Удачи! 🍀"
        )
        await message.answer(text, reply_markup=None)
    else:
        name = quiz_names[quiz_id - 1]
        text = f"Сейчас активен квиз «{name}». Вы можете присоединиться к нему."
        await message.answer(text, reply_markup=markup)

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
    remove_kb = ReplyKeyboardBuilder().as_markup(remove_keyboard=True)
    # отправим невидимый символ, чтобы просто убрать клавиатуру
    await message.answer("Квиз начат. Удачи! 🍀", reply_markup=remove_kb)
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
    # удаляем прошлый вопрос (если есть)
    last_msg = data.get("last_question_message_id")
    if last_msg:
        try:
            await bot.delete_message(chat_id, last_msg)
        except:
            pass
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

    await state.update_data(last_question_message_id=msg.message_id)

    # стартуем задачу-таймер и сохраняем её, чтобы можно было отменить
    timer_task = asyncio.create_task(
        start_timer(bot, chat_id, msg.message_id, idx, state)
    )
    await state.update_data(timer_task=timer_task)


async def finish_quiz(chat_id: int, state: FSMContext):
    data = await state.get_data()
    answers = data["answers"]
    start = data["start_time"]
    last_msg = data.get("last_question_message_id")
    if last_msg:
        try:
            await bot.delete_message(chat_id, last_msg)
        except:
            pass
    quiz_id = data["quiz_id"]
    questions = quiz_sets[quiz_id-1]
    total_q = len(questions)
    answers = answers[:total_q]
    total_time = time.time() - start
    correct = sum(
        1
        for i, ua in enumerate(answers)
        if ua == quiz_sets[data["quiz_id"] - 1][i]["answer"]
    )

    # сохраняем
    db.save_result(chat_id, data["quiz_id"], correct, total_time)

    # формируем отчет
    report = (
        f"🎉 Квиз завершён!\n"
        f"✅ Правильных: {correct}/{len(answers)}\n"
        f"⏱️ Время: {int(total_time)} сек\n\n"
    )
    for i, ua in enumerate(answers):
        q = quiz_sets[data["quiz_id"] - 1][i]
        user_answer = "–" if ua is None else q["options"][ua]
        correct_answer = q["options"][q["answer"]]
        report += (
            f"{i+1}. {q['question']}\n"
            f"   Ваш ответ: {user_answer}\n"
            f"   Правильный: {correct_answer}\n\n"
        )

    # отправляем пользователю
    await bot.send_message(chat_id, report)
    # убираем клавиатуру
    await bot.send_message(
        chat_id,
        "Спасибо за участие! Ждите запуска следующего квиза.",
        reply_markup=ReplyKeyboardBuilder().as_markup(remove_keyboard=True)
    )

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
        await finish_quiz(callback.from_user.id, state)
#         start = data["start_time"]
#         total_time = time.time() - start
#         correct = sum(
#             1
#             for i, user_ans in enumerate(answers)
#             if user_ans == quiz_sets[data["quiz_id"]-1][i]["answer"]
#         )
#
#         # сохраняем в БД
#         db.save_result(callback.from_user.id, data["quiz_id"], correct, total_time)
#
#         # формируем и отсылаем отчёт
#         report = (
#             f"🎉 Квиз завершён!\n"
#             f"✅ Правильных: {correct}/{total_questions}\n"
#             f"⏱️ Время: {int(total_time)} сек\n\n"
#         )
#         for i, user_ans in enumerate(answers):
#             q = quiz_sets[data["quiz_id"]-1][i]
#             ua = "–" if user_ans is None else q["options"][user_ans]
#             ca = q["options"][q["answer"]]
#             report += (
#                 f"{i+1}. {q['question']}\n"
#                 f"   Ваш ответ: {ua}\n"
#                 f"   Правильный: {ca}\n\n"
#             )
#         await bot.send_message(callback.from_user.id, report)
#         # сообщаем об окончании и убираем кнопки
#         await bot.send_message(
#             callback.from_user.id,
#             "Спасибо за участие! Ждите запуска следующего квиза.",
#             reply_markup=ReplyKeyboardBuilder().as_markup(remove_keyboard=True)
#         )

@dp.message(lambda message: message.text == "Начать квиз")
async def start_quiz_text(message: Message, state: FSMContext):
    # просто делегируем логику существующему хендлеру
    await start_quiz_user(message, state)

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
    # кнопка для участников
    kb = ReplyKeyboardBuilder()
    kb.button(text="Начать квиз")
    kb.adjust(1)
    markup = kb.as_markup(resize_keyboard=True)
    # рассылаем всем зарегистрированным
    name = quiz_names[num - 1]
    for uid in db.get_all_users():
        try:
            await bot.send_message(
                uid,
                f"🔔 Квиз «{name}» начат! Нажмите «Начать квиз», чтобы участвовать.",
                reply_markup=markup
            )
        except:
            pass

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
