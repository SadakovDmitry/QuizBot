import os

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '7829651867:AAHmlsr4xEluhZpGLTbz1qpCVn7ijMIPiwY')

# Список администраторов (Telegram user_id)
ADMIN_IDS = {1037664248, 0000000000}

# Путь к базе данных SQLite
DB_PATH = 'quiz.db'

# Продолжительность вопроса в секундах
QUESTION_TIME = 60
# Интервал обновления таймера в секундах
TIMER_INTERVAL = 5
