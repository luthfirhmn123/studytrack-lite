from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_db, init_db

app = FastAPI()
init_db()

class CourseIn(BaseModel):
    name: str

class TaskIn(BaseModel):
    course_id: int
    title: str
    due_at: str | None = None

@app.get("/")
def home():
    return {"message": "hello"}

@app.post("/courses")
def create_course(course: CourseIn):
    conn = get_db()
    cur = conn.execute("INSERT INTO courses (name) VALUES (?)", (course.name,))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "name": course.name}

@app.get("/courses")
def list_courses():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM courses ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/tasks")
def create_task(task: TaskIn):
    conn = get_db()
    course = conn.execute(
        "SELECT id FROM courses WHERE id = ?", (task.course_id,)
    ).fetchone()
    if course is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Course not found")
    cur = conn.execute(
        "INSERT INTO tasks (course_id, title, due_at) VALUES (?, ?, ?)",
        (task.course_id, task.title, task.due_at),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {
        "id": new_id,
        "course_id": task.course_id,
        "title": task.title,
        "due_at": task.due_at,
        "is_done": False,
    }