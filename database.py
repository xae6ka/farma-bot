import aiosqlite

DB_NAME = "main.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pill_id INTEGER NOT NULL,
                time TEXT NOT NULL,
                FOREIGN KEY (pill_id) REFERENCES pills(id) ON DELETE CASCADE
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS dose_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pill_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                scheduled_date TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (pill_id) REFERENCES pills(id) ON DELETE CASCADE,
                UNIQUE(pill_id, scheduled_date, scheduled_time)
            )
        """)

        await db.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        deadline TEXT NOT NULL
                    )
                """)

        await db.commit()


async def add_user(user_id: int, first_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (user_id, first_name)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET first_name = excluded.first_name
        """, (user_id, first_name))

        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT user_id, first_name
            FROM users
        """)

        return await cursor.fetchall()

async def add_pill(user_id: int, name: str, times: list[str]):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO pills (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        pill_id = cursor.lastrowid

        for time in times:
            await db.execute(
                "INSERT INTO schedules (pill_id, time) VALUES (?, ?)",
                (pill_id, time)
            )

        await db.commit()
        return pill_id


async def get_pills(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT p.id, p.name, s.time
            FROM pills p
            LEFT JOIN schedules s ON p.id = s.pill_id
            WHERE p.user_id = ?
            ORDER BY p.id, s.time
        """, (user_id,))
        return await cursor.fetchall()


async def get_pill(user_id: int, pill_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT p.id, p.name, s.time
            FROM pills p
            LEFT JOIN schedules s ON p.id = s.pill_id
            WHERE p.id = ? AND p.user_id = ?
            ORDER BY s.time
        """, (pill_id, user_id))
        return await cursor.fetchall()


async def delete_pill(user_id: int, pill_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM pills WHERE id = ? AND user_id = ?",
            (pill_id, user_id)
        )
        if not await cursor.fetchone():
            return False

        await db.execute("DELETE FROM dose_events WHERE pill_id = ?", (pill_id,))
        await db.execute("DELETE FROM schedules WHERE pill_id = ?", (pill_id,))
        await db.execute(
            "DELETE FROM pills WHERE id = ? AND user_id = ?",
            (pill_id, user_id)
        )
        await db.commit()
        return True


async def update_schedule(user_id: int, pill_id: int, times: list[str]):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM pills WHERE id = ? AND user_id = ?",
            (pill_id, user_id)
        )
        if not await cursor.fetchone():
            return False

        await db.execute(
            "DELETE FROM dose_events WHERE pill_id = ? AND status != 'taken'",
            (pill_id,)
        )
        await db.execute("DELETE FROM schedules WHERE pill_id = ?", (pill_id,))

        for time in times:
            await db.execute(
                "INSERT INTO schedules (pill_id, time) VALUES (?, ?)",
                (pill_id, time)
            )

        await db.commit()
        return True


async def get_all_schedules():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT p.id, p.user_id, p.name, s.id, s.time
            FROM pills p
            JOIN schedules s ON p.id = s.pill_id
            ORDER BY p.id, s.time
        """)
        return await cursor.fetchall()


async def get_or_create_dose_event(
    pill_id: int,
    user_id: int,
    scheduled_date: str,
    scheduled_time: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, status
            FROM dose_events
            WHERE pill_id = ? AND scheduled_date = ? AND scheduled_time = ?
        """, (pill_id, scheduled_date, scheduled_time))
        event = await cursor.fetchone()

        if event:
            return event

        cursor = await db.execute("""
            INSERT INTO dose_events (
                pill_id, user_id, scheduled_date, scheduled_time, status
            ) VALUES (?, ?, ?, ?, 'pending')
        """, (pill_id, user_id, scheduled_date, scheduled_time))
        event_id = cursor.lastrowid
        await db.commit()
        return event_id, "pending"


async def get_dose_event(event_id: int, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT de.id, de.pill_id, de.user_id, de.scheduled_date,
                   de.scheduled_time, de.status, p.name
            FROM dose_events de
            JOIN pills p ON p.id = de.pill_id
            WHERE de.id = ? AND de.user_id = ?
        """, (event_id, user_id))
        return await cursor.fetchone()


async def mark_dose_taken(event_id: int, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            UPDATE dose_events
            SET status = 'taken'
            WHERE id = ? AND user_id = ? AND status != 'taken'
        """, (event_id, user_id))
        await db.commit()
        return cursor.rowcount > 0


async def mark_dose_snoozed(event_id: int, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            UPDATE dose_events
            SET status = 'snoozed'
            WHERE id = ? AND user_id = ? AND status != 'taken'
        """, (event_id, user_id))
        await db.commit()
        return cursor.rowcount > 0


async def get_active_dose_events():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT de.id, de.pill_id, de.user_id, de.scheduled_date,
                   de.scheduled_time, de.status, p.name
            FROM dose_events de
            JOIN pills p ON p.id = de.pill_id
            WHERE de.status != 'taken'
        """)
        return await cursor.fetchall()


#db for tasks
async def add_tasks(user_id: int, name: str, deadline: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO tasks (user_id, name, deadline) VALUES (?, ?, ?)",
            (user_id, name, deadline)
        )

        await db.commit()


async def get_tasks(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT t.id, t.name, t.deadline
            FROM tasks t
            WHERE t.user_id = ?
        """, (user_id,))
        return await cursor.fetchall()

async def delete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        await db.commit()
        return True