# db.py
import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
                                user_id INTEGER PRIMARY KEY,
                                question_index INTEGER
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS user_answers (
                                user_id INTEGER,
                                question_index INTEGER,
                                user_answer TEXT,
                                correct_answer TEXT,
                                is_correct INTEGER
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS user_statistics (
                                user_id INTEGER PRIMARY KEY,
                                best_score INTEGER DEFAULT 0,
                                attempts INTEGER DEFAULT 0
                            )''')
        await db.commit()

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO quiz_state (user_id, question_index)
                            VALUES (?, ?)''', (user_id, index))
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def save_user_answer(user_id, question_index, user_answer, correct_answer, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT INTO user_answers (user_id, question_index, user_answer, correct_answer, is_correct)
                            VALUES (?, ?, ?, ?, ?)''', 
                         (user_id, question_index, user_answer, correct_answer, is_correct))
        await db.commit()

async def reset_user_progress(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
        await db.execute('DELETE FROM user_answers WHERE user_id = ?', (user_id,))
        await db.commit()

async def update_user_statistics(user_id, score):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT best_score FROM user_statistics WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            best_score = row[0] if row else 0
            
        is_new_record = score > best_score
        new_best_score = max(score, best_score)

        await db.execute('''INSERT INTO user_statistics (user_id, best_score, attempts)
                            VALUES (?, ?, 1)
                            ON CONFLICT(user_id) DO UPDATE SET
                            best_score = ?,
                            attempts = attempts + 1''',
                         (user_id, new_best_score, new_best_score))
        await db.commit()

    return is_new_record, new_best_score

async def get_top_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT user_id, best_score, attempts
                                 FROM user_statistics
                                 ORDER BY best_score DESC, attempts DESC
                                 LIMIT 10''') as cursor:
            rows = await cursor.fetchall()
            return rows
