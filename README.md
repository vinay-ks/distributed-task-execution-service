# Distributed Task Execution Service

## Overview
A backend service that accepts tasks via REST APIs, executes them asynchronously
in the background using controlled concurrency, and tracks task state persistently.

## Features
- REST APIs to create and query tasks
- Asynchronous background execution using thread pools
- Persistent task storage with PostgreSQL
- Task lifecycle management (PENDING, RUNNING, COMPLETED, FAILED)
- Retry logic with bounded retries
- Crash recovery on service restart
- Automated API tests

## Tech Stack
- Python, FastAPI
- PostgreSQL, SQLAlchemy
- ThreadPoolExecutor for concurrency
- Pytest for testing

## How to Run
1. Install dependencies
2. Start PostgreSQL
3. Run `uvicorn app.main:app --reload`
4. Open `/docs` for API testing
