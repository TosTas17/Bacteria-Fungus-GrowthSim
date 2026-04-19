FROM python:3.12-slim

WORKDIR /app

COPY requirementsWS.txt .

RUN pip install --no-cache-dir -r requirementsWS.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]