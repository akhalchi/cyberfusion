import aio_pika




async def send_response(output_queue_name: str, message_json: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()

    message_body_encoded = message_json.encode()
    await channel.default_exchange.publish(
        aio_pika.Message(body=message_body_encoded),
        routing_key=output_queue_name,
    )
    print(f"Sent message to queue '{output_queue_name}': {message_json}")