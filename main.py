from fastapi import FastAPI
from db import init_db

app = FastAPI()
init_db()

@app.get("/")
def home():
    return {"message": "hello"}