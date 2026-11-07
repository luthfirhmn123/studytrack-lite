from fastapi import FastAPI
from pydantic import BaseModel
from db import get_db, init_db

app = FastAPI()
init_db()

class CourseIn(BaseModel):
    name: str

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