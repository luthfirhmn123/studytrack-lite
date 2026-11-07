import sqlite3

def get_db():
    conn = sqlite3.connect("studytrack.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        due_at TEXT,
        is_done INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (course_id) REFERENCES courses(id))""")
    conn.commit()
    conn.close()