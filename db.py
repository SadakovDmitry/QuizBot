import sqlite3
from config import DB_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id INTEGER,
                correct_count INTEGER,
                total_time REAL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                active_quiz_id INTEGER
            )
        ''')
        # Таблица для фиксации начала квиза
        cur.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_id INTEGER,
                start_time REAL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        # Инициализация единственной строки
        cur.execute('INSERT OR IGNORE INTO quiz_state(id, active_quiz_id) VALUES (1, NULL)')
        self.conn.commit()

    def register_user(self, user_id: int, first_name: str, last_name: str):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users(user_id, first_name, last_name) VALUES (?, ?, ?)",
            (user_id, first_name, last_name)
        )
        self.conn.commit()

    def get_active_quiz(self):
        cur = self.conn.cursor()
        cur.execute('SELECT active_quiz_id FROM quiz_state WHERE id = 1')
        row = cur.fetchone()
        return row['active_quiz_id'] if row else None

    def set_active_quiz(self, quiz_id: int | None):
        cur = self.conn.cursor()
        cur.execute('UPDATE quiz_state SET active_quiz_id = ? WHERE id = 1', (quiz_id,))
        self.conn.commit()

    def has_played(self, user_id: int, quiz_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM results WHERE user_id = ? AND quiz_id = ?",
            (user_id, quiz_id)
        )
        return cur.fetchone() is not None

    def save_result(self, user_id: int, quiz_id: int, correct: int, total_time: float):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO results(user_id, quiz_id, correct_count, total_time) VALUES (?, ?, ?, ?)",
            (user_id, quiz_id, correct, total_time)
        )
        self.conn.commit()

    def get_results(self, quiz_id: int):
        cur = self.conn.cursor()
        cur.execute(
            '''
            SELECT u.first_name, u.last_name, r.correct_count, r.total_time
            FROM results r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.quiz_id = ?
            ORDER BY r.correct_count DESC, r.total_time ASC
            ''',
            (quiz_id,)
        )
        return cur.fetchall()

    def record_start(self, user_id: int, quiz_id: int, start_time: float):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO attempts(user_id, quiz_id, start_time) VALUES (?, ?, ?)",
            (user_id, quiz_id, start_time)
        )
        self.conn.commit()

    def get_started_count(self, quiz_id: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT COUNT(DISTINCT user_id) AS cnt FROM attempts WHERE quiz_id = ?",
            (quiz_id,)
        )
        row = cur.fetchone()
        return row["cnt"] if row else 0


# Создаем единый экземпляр
db = Database()
