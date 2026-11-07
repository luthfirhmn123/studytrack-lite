from datetime import datetime
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

@app.get("/tasks")
def list_tasks():
    conn = get_db()
    rows = conn.execute(
        """SELECT tasks.id, tasks.course_id, courses.name AS course_name,
                  tasks.title, tasks.due_at, tasks.is_done
           FROM tasks
           JOIN courses ON courses.id = tasks.course_id
           ORDER BY tasks.id"""
    ).fetchall()
    conn.close()
    tasks = []
    for row in rows:
        task = dict(row)
        task["is_done"] = bool(task["is_done"])
        tasks.append(task)
    return tasks

class TaskUpdate(BaseModel):
    course_id: int | None = None
    title: str | None = None
    due_at: datetime | None = None
    is_done: bool | None = None

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, changes: TaskUpdate):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    course_id = changes.course_id if changes.course_id is not None else task["course_id"]
    title = task["title"]
    if changes.title is not None:
        title = changes.title.strip()
        if not title:
            conn.close()
            raise HTTPException(status_code=422, detail="Title cannot be empty")
    due = changes.due_at.isoformat() if changes.due_at is not None else task["due_at"]
    is_done = int(changes.is_done) if changes.is_done is not None else task["is_done"]

    course = conn.execute("SELECT id FROM courses WHERE id = ?", (course_id,)).fetchone()
    if course is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Course not found")

    conn.execute(
        "UPDATE tasks SET course_id = ?, title = ?, due_at = ?, is_done = ? WHERE id = ?",
        (course_id, title, due, is_done, task_id),
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "course_id": course_id, "title": title,
            "due_at": due, "is_done": bool(is_done)}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": task_id}