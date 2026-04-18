import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def publish_simulation(data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )

    channel = connection.channel()

    channel.queue_declare(queue="simulation_queue", durable=True)

    print("Publishing:", data)


    channel.basic_publish(
        exchange="",
        routing_key="simulation_queue",
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2  # persistente
        )
    )

  

    print("Sent!")

    connection.close()