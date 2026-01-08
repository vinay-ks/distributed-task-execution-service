from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Distributed Task Execution Service is running"}
