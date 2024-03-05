import asyncio
import aio_pika
from repository import db,add_task_to_db,get_tasks_from_db
from rabbitmq import send_response
import json


async def main():
    await db()
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()


    get_tasks = await channel.declare_queue("get_tasks_request", durable=True)
    add_task = await channel.declare_queue("add_task_request", durable=True)

    async def consume(queue):
        async for message in queue:
            async with message.process():
                message_body = message.body.decode()
                if queue.name == "get_tasks_request":
                    print(f"Received message '{message_body}' from ",queue.name)
                    response_tasks = await get_tasks_from_db(message)
                    print(response_tasks)
                    await send_response("get_tasks_response",response_tasks)
                elif queue.name == "add_task_request":
                    print(f"Received message '{message_body}' from ",queue.name)
                    response_data = await add_task_to_db(message)
                    data_json = json.dumps({"status": response_data[0], "task_id": response_data[1]})
                    await send_response("add_task_response",data_json)
                    print(response_data)

    await asyncio.gather(
        consume(get_tasks),
        consume(add_task)
    )

if __name__ == "__main__":
    asyncio.run(main())

