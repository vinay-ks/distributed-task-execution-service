import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from app.models import Task
from app.db import SessionLocal

import random
random.seed(12345)

MAX_RETRIES = 2

executor = ThreadPoolExecutor(max_workers=4)


def execute_task(task_id):
    db: Session = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        task.status = "RUNNING"
        db.commit()

        time.sleep(3)

        # Simulate a 50% chance of failure
        if random.random() < 0.5:
            raise RuntimeError("Simulated failure")

        task.status = "COMPLETED"
        db.commit()

    except Exception:
        # IMPORTANT: reload task in a fresh state
        db.rollback()

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        task.retry_count += 1

        if task.retry_count <= MAX_RETRIES:
            task.status = "PENDING"
            db.commit()
            executor.submit(execute_task, task.id)
        else:
            task.status = "FAILED"
            db.commit()

    finally:
        db.close()
