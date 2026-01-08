import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from app.models import Task
from app.db import SessionLocal

# Thread pool for concurrent task execution
executor = ThreadPoolExecutor(max_workers=4)


def execute_task(task_id):
    """
    Background task execution logic.
    Runs in a separate thread.
    """
    db: Session = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        # Mark task as RUNNING
        task.status = "RUNNING"
        db.commit()

        # Simulate actual work
        time.sleep(50)

        # Mark task as COMPLETED
        task.status = "COMPLETED"
        db.commit()

    except Exception:
        # On failure, mark task as FAILED
        task.status = "FAILED"
        db.commit()
    finally:
        db.close()
