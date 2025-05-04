from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup


def make_options_keyboard(options: list[str], question_idx: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        builder.button(text=opt, callback_data=f"answer_{question_idx}_{i}")
    builder.adjust(1)
    return builder.as_markup()

async def start_timer(
    bot: Bot,
    chat_id: int,
    message_id: int,
    question_idx: int,
    state,
):
    """
    Каждые 5 сек обновляет сообщение с оставшимся временем.
    Если после цикла флаг 'answered' не поднят — автопереход по таймауту.
    """
    for remaining in range(60, 0, -5):
        await asyncio.sleep(5)
        data = await state.get_data()
        if data.get("answered", False):
            return  # пользователь уже ответил, выходим

        # обновляем текст
        q = data["current_question"]
        kb = data["current_keyboard"]
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"❓ Вопрос {question_idx+1}: {q['question']}\n🕒 Осталось {remaining-5} сек",
                reply_markup=kb,
            )
        except:
            return  # например, сообщение удалили

#     # Таймаут: помечаем как отвеченный, добавляем None в ответы
#     await state.update_data(answered=True)
#     answers = data.get("answers", [])
#     answers.append(None)  # None будет считаться неверным
#     await state.update_data(answers=answers)
#
#     # запускаем следующий вопрос
#     await ask_question(chat_id, state)
    # Время вышло — заново подтягиваем state
    from main import ask_question, finish_quiz, quiz_sets
    data = await state.get_data()
    if data.get("answered", False):
        return  # на грани успел нажать

    # 1) засчитываем None как ответ
    answers = data.get("answers", [])
    answers.append(None)
    # 2) помечаем answered, чтобы следующий таймер не сработал
    curr_idx = data.get("current_idx", 0)
    next_idx = curr_idx + 1
    await state.update_data(
        answers=answers,
        answered=True,
        current_idx=next_idx
    )

    # 3) если есть следующий вопрос — задаем его
    quiz_id = data["quiz_id"]
    total_q = len(quiz_sets[quiz_id - 1])
    if next_idx < total_q:
        await ask_question(chat_id, state)
    else:
        # 4) иначе — завершаем квиз той же логикой, что и в callback
        await finish_quiz(chat_id, state)
