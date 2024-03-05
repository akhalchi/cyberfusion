import asyncio
import aio_pika


async def process_messages(input_queue_name: str, output_queue_name: str, message_data: str) -> str:
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()


    await channel.default_exchange.publish(
        aio_pika.Message(body=message_data.encode()),
        routing_key=output_queue_name,
    )
    print(f"Sent message to queue '{output_queue_name}': {message_data}")

    input_queue = await channel.declare_queue(input_queue_name, durable=True)

    try:
        await asyncio.sleep(3)
        incoming_message = await asyncio.wait_for(input_queue.get(), timeout=5)
        response_body = incoming_message.body.decode()
        print(f"Received message from queue '{input_queue_name}': {response_body}")
        await incoming_message.ack()
        return response_body
    except asyncio.TimeoutError:
        print("No response from RabbitMQ within 5 seconds.")
        return "No response from RabbitMQ within 5 seconds."
    except aio_pika.exceptions.QueueEmpty:
        print("Queue is empty. No message received.")
        return "Queue is empty. No message received."
    finally:
        await connection.close()
