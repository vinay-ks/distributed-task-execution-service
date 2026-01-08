import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from app.models import Task
from app.db import SessionLocal
from app.metrics import metrics

import random
random.seed(12345)

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

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
        logger.info(f"Task {task_id} started execution")

        time.sleep(3)

        # Simulate a 50% chance of failure
        if random.random() < 0.5:
            raise RuntimeError("Simulated failure")

        task.status = "COMPLETED"
        db.commit()
        logger.info(f"Task {task_id} completed successfully")
        metrics["tasks_completed"] += 1


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
            logger.warning(
                f"Task {task_id} failed, retry {task.retry_count}/{MAX_RETRIES}"
            )
            executor.submit(execute_task, task.id)
            metrics["tasks_retried"] += 1
        else:
            task.status = "FAILED"
            db.commit()
            logger.error(f"Task {task_id} permanently failed")
            metrics["tasks_failed"] += 1

    finally:
        db.close()
