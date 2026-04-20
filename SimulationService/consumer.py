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

    print(f"[+] Received start request for simulation {sim_id}")

    db = SessionLocal()

    try:
   
        sim = db.query(Simulation).filter_by(id=sim_id).first()

        if not sim:
            print("Simulation not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        model = sim.model
        N0 = sim.initial_population
        r = sim.growth_rate
        steps = sim.steps
        K = sim.carrying_capacity

        print(f"[+] Processing simulation {sim_id}")

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
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        total_steps = len(result)

        for i, point in enumerate(result):

            # guardar na DB
            db.add(SimulationResult(
                simulation_id=sim_id,
                time=point["time"],
                population=point["population"]
            ))

            # calcular progresso (%)
            progress = int((i + 1) / total_steps * 100)
    
            # enviar update para RabbitMQ
            ch.basic_publish(
                exchange='',
                routing_key='simulation_updates',
                body=json.dumps({
                    "simulation_id": sim_id,
                    "time": point["time"],
                    "population": point["population"],
                    "progress": progress
                })
            )

            print("publishing",json.dumps({
                    "simulation_id": sim_id,
                    "time": point["time"],
                    "population": point["population"],
                    "progress": progress
                }))

    
        sim.status = "completed"
        sim.finished_at = datetime.now(timezone.utc)


        db.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag)

        print(f"[✔] Finished simulation {sim_id}")

    except Exception as e:
        print(f"[!] Error processing simulation {sim_id}: {e}")

        
        sim = db.query(Simulation).filter_by(id=sim_id).first()
        if sim:
            sim.status = "failed"
            sim.finished_at = datetime.now(timezone.utc)
            db.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    finally:
        db.close()



def start_consumer():
    while True:
        try:
            connection = connect()
            channel = connection.channel()

           
            channel.queue_declare(queue='simulation_start', durable=True)
            channel.queue_declare(queue='simulation_updates', durable=True)

            channel.basic_consume(
                queue='simulation_start',
                on_message_callback=callback,
                auto_ack=False
            )


            print("[*] Waiting for simulation start requests...")
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