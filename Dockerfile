FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY scripts /app/scripts
COPY dashboard /app/dashboard
COPY run_engine.sh /app/run_engine.sh

RUN chmod +x /app/run_engine.sh

CMD ["/app/run_engine.sh"]
