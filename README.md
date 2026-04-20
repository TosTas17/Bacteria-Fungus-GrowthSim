# 🧫 SimulatorB.io - Bacteria/Fungus Growth Simulator in microservices

A scalable, asynchronous simulation system based on an event-driven architecture, focused on resilience and decoupling.

## 🏗️ System Architecture

The system consists of decoupled services, all in docker containers within the same docker network, that communicate through a message broker.

<img src="./architecture_design.png" alt="Architecture Diagram"/>

### Workflow
1. **API:** Receives the request via `POST /simulate`, creates a record in the DB (status `pending`), and publishes an event.
2. **RabbitMQ:** Acts as the broker, ensuring messages are persistent (`durable=True`).
3. **Workers:** Consume from the `simulation_start`, process the simulation, and publish results on `simulation_updates`.
4. **WebSocket Service:** Sends start signal to `simulation_start`, receives updates from the workers in `simulation_updates` and delivers them in real-time to the client.

**Resilience Features:**
* **`auto_ack=False`**: If a worker crashes during processing, the message returns to the queue, ensuring no data loss.
* **Decoupling:** The WebSocket service and the workers are agnostic to each other, allowing for independent horizontal scaling of compute resources.

---

## 🛠️ Operational Commands

### Docker Compose
The images will be pulled from the GitHub repo:
```bash
docker compose pull
docker compose up
```
---

## 🌐 Local Development Setup (Domain)

To access the application via `http://simulatorb.io` in your browser, you must map the domain to your local machine in your `hosts` file.

### 1. Edit your hosts file
Open your hosts file with administrative privileges:

* **Linux / macOS:** `/etc/hosts`
* **Windows:** `C:\Windows\System32\drivers\etc\hosts`

### 2. Add the following line:
```text
127.0.0.1   simulatorb.io
```

### 3. Access the application
Once saved, you can open your browser and navigate to:
**`http://simulatorb.io`**

---

### Accessing the Database
To inspect the PostgreSQL tables:
```bash
docker exec -it simulation-db psql -U sim_user -d simulation_db

                    List of relations
 Schema |           Name            |   Type   |  Owner   
--------+---------------------------+----------+----------
 public | simulation_results        | table    | sim_user
 public | simulations               | table    | sim_user

simulations_results table keeps the results of the simulations
simulations keeps the metadata (the parameters for simulation) and timestamps
```

---

## 📋 Implemented Features

* **Queue Persistence:** Messages survive RabbitMQ restarts.
* **Fault Tolerance:** Automatic task re-enqueuing in the event of a worker failure.
* **Horizontal Scalability:** Ability to scale workers independently.
* **Status API:** Endpoint for monitoring simulation states (pending/running).
* **Asynchronous Communication:** Event-driven architecture using a message broker.
* **Real-Time Visualization:** Provides interactive frontend charts that reflect simulation progress instantly as data is processed by the backend.
* **Database:** Structured storage for simulation metadata, timestamps, and results.
* **GitHub Actions:** Automated image building and management, with simplified deployment via the GitHub Container Registry.

---

## ⚙️ Tech Stack
* **Backend:** FastAPI (Python)
* **Frontend:** React (Vite), Tailwind, TypeScript
* **Broker:** RabbitMQ
* **Database:** PostgreSQL
* **Proxy:** Nginx
* **Real time communication:** WebSockets 

---