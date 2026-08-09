FROM python:3.13-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY .env.example /app/.env.example
COPY scripts /app/scripts
COPY dashboard /app/dashboard
COPY .streamlit /app/.streamlit
COPY run_engine.sh /app/run_engine.sh

RUN chmod +x /app/run_engine.sh

CMD ["/app/run_engine.sh"]
