import pika
import json
import os
import time

from SimulationService.simulator import exponential_growth, logistic_growth
from DataBase.database import SessionLocal
from DataBase.db_models import SimulationResult

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")


def callback(ch, method, properties, body):

    
    data = json.loads(body)

    sim_id = data["simulation_id"]
    model = data["model"]
    N0 = data["initial_population"]
    r = data["growth_rate"]
    steps = data["steps"]
    K = data.get("carrying_capacity")

    print(f"[+] Processing simulation {sim_id}")

    # correr simulação
    if model == "exponential":
        result = exponential_growth(N0, r, steps)

    elif model == "logistic":
        result = logistic_growth(N0, r, K, steps)

    else:
        print("Invalid model")
        return

    # guardar na DB
    db = SessionLocal()

    for point in result:
        db.add(SimulationResult(
            simulation_id=sim_id,
            time=point["time"],
            population=point["population"]
        ))

    db.commit()
    db.close()

    print(f"[✔] Finished simulation {sim_id}")



def start_consumer():
    while True:
        try:
            connection = connect()
            channel = connection.channel()

            channel.queue_declare(queue='simulation_queue',durable=True)

            channel.basic_consume(
                queue='simulation_queue',
                on_message_callback=callback,
                auto_ack=True
            )

            print("[*] Waiting for messages...")
            channel.start_consuming()

        except Exception as e:
            import traceback
            print("[!] Error:", repr(e))
            traceback.print_exc()
            time.sleep(5)

def connect():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            return connection
        except Exception as e:
            print("[!] RabbitMQ not ready, retrying...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()