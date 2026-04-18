import pika
import json
import os
import time

from SimulationService.simulator import exponential_growth, logistic_growth
from DataBase.database import SessionLocal
from DataBase.db_models import SimulationResult, Simulation

from datetime import datetime, timezone


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

    db = SessionLocal()

    try:
   
        sim = db.query(Simulation).filter_by(id=sim_id).first()

        if not sim:
            print("Simulation not found")
            return

   
        sim.status = "running"
        sim.started_at = datetime.now(timezone.utc)
        db.commit()

        # correr simulação
        if model == "exponential":
            result = exponential_growth(N0, r, steps)

        elif model == "logistic":
            result = logistic_growth(N0, r, K, steps)

        else:
            print("Invalid model")
            sim.status = "failed"
            db.commit()
            return

        # guardar resultados
        for point in result:
            db.add(SimulationResult(
                simulation_id=sim_id,
                time=point["time"],
                population=point["population"]
            ))

    
        sim.status = "completed"
        sim.finished_at = datetime.now(timezone.utc)


        db.commit()

        print(f"[✔] Finished simulation {sim_id}")

    except Exception as e:
        print(f"[!] Error processing simulation {sim_id}: {e}")

        
        sim = db.query(Simulation).filter_by(id=sim_id).first()
        if sim:
            sim.status = "failed"
            sim.finished_at = datetime.now(timezone.utc)
            db.commit()

    finally:
        db.close()



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