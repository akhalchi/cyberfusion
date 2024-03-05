from sqlalchemy import select
import aio_pika
from database import new_session, TaskOrm
from schemas import STaskAdd, STask
from database import create_tables
import json
from typing import Tuple


class TaskRepository:
    @classmethod
    async def add_one(cls, data: STaskAdd) -> int:
        async with new_session() as session:
            task_dict = data.model_dump()

            task = TaskOrm(**task_dict)
            session.add(task)
            await session.flush()
            await session.commit()
            return task.id

    @classmethod
    async def find_all(cls) -> list[STask]:
        async with new_session() as session:
            query = select(TaskOrm)
            result = await session.execute(query)
            task_models = result.scalars().all()
            task_schemas = [STask.model_validate(task_model) for task_model in task_models]
            return task_schemas

async def db():
    await create_tables()
    print("Database is ready")

async def add_task_to_db(message: aio_pika.IncomingMessage)->Tuple[str, int]:
        message_body = message.body.decode()
        name_start = message_body.index("name='") + len("name='")
        name_end = message_body.index("'", name_start)
        name = message_body[name_start:name_end]

        description_start = message_body.index("description='") + len("description='")
        description_end = message_body.index("'", description_start)
        description = message_body[description_start:description_end]

        # Создаем объект STaskAdd
        task_data = STaskAdd(name=name, description=description)
        task_id = await TaskRepository.add_one(task_data)
        return "added", task_id

async def get_tasks_from_db(message: aio_pika.IncomingMessage) -> str:

        try:
            tasks = await TaskRepository.find_all()
            tasks_json = [task.dict() for task in tasks]
            print("All tasks was sent")
            return json.dumps(tasks_json)
        except Exception as e:
            error_message = {"error": str(e)}
            print("Error while retrieving tasks from the database:", error_message)
            return json.dumps(error_message)