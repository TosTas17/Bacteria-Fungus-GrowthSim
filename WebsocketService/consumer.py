import pika
import json
import os
import asyncio

from manager import manager

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def start_consumer():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

  
    channel.queue_declare(queue='simulation_updates', durable=True)

    print("[WS] Waiting for simulation updates...")

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)

            sim_id = data.get("simulation_id")

            print(f"[WS] Update for simulation {sim_id}: {data}")

            # enviar para websocket (async dentro de sync)
            asyncio.run(manager.send(sim_id, data))

        except Exception as e:
            print(f"[WS ERROR] {e}")

    channel.basic_consume(
        queue='simulation_updates',
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()