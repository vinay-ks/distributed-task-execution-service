from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from contextlib import asynccontextmanager # Added for lifespan

from app.db import SessionLocal
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.services.executor import executor, execute_task

# --- Lifespan Manager (Replaces @app.on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on Startup
    db = SessionLocal()
    try:
        # 1. Find everything that isn't COMPLETED or FAILED
        unfinished_tasks = db.query(Task).filter(
            Task.status.in_(["RUNNING", "PENDING"])
        ).all()
        
        if unfinished_tasks:
            task_ids = [t.id for t in unfinished_tasks]
            
            # 2. Reset everything to PENDING (so they are ready for a fresh start)
            db.query(Task).filter(Task.id.in_(task_ids)).update({"status": "PENDING"})
            db.commit()
            
            # 3. Re-submit all of them to the thread pool
            for tid in task_ids:
                executor.submit(execute_task, tid)
                print(f"Queued task for execution: {tid}")
    except Exception as e:
        print(f"Recovery failed: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield  # Server runs here
    
    # This runs on Shutdown
    executor.shutdown(wait=True)

# Initialize app with lifespan
app = FastAPI(lifespan=lifespan)

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Distributed Task Execution Service is running"}


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        name=task.name,
        status="PENDING"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Submit task for background execution
    executor.submit(execute_task, new_task.id)

    return new_task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
