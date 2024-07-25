import aiosqlite

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    async def init_db(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    settings TEXT
                )
            ''')
            await db.commit()

    async def add_user(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (user_id, settings) VALUES (?, ?)
            ''', (user_id, '{}'))
            await db.commit()

    async def update_settings(self, user_id, settings):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE users SET settings = ? WHERE user_id = ?
            ''', (settings, user_id))
            await db.commit()

    async def get_settings(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT settings FROM users WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else '{}'

    async def user_exists(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('''
                SELECT 1 FROM users WHERE user_id = ?
            ''', (user_id,)) as cursor:
                return await cursor.fetchone() is not None

