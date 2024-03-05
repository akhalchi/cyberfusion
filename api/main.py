from fastapi import FastAPI,Depends
from schemas import STaskAdd
from rabbitmq import process_messages
import json


app = FastAPI()
@app.get("/test")
async def home():
    return {"data": "Hello World"}

@app.post("/")
async def add_task_to_rabbitmq(task_data: STaskAdd = Depends()):
    task = str(task_data)
    response = await process_messages("add_task_response", "add_task_request",task)
    return {response}

@app.get("/tasks")
async def get_all_tasks():
    response = await process_messages("get_tasks_response", "get_tasks_request","get_tasks")
    return {response}