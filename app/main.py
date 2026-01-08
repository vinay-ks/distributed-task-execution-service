from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Task

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Distributed Task Execution Service is running"}


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks
