FROM python:3.11

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "poligon_it", "worker", "--loglevel=info"]
