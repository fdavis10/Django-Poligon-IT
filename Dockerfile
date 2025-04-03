<<<<<<< HEAD
FROM python:3.9-slim
=======
FROM python:3.12
>>>>>>> 3281c1d (production)

WORKDIR /app

<<<<<<< HEAD
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


WORKDIR /app
COPY . /app/


RUN pip install -r requirements.txt

=======
COPY . .

ENV PYTHONPATH=/app/backend

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN chmod +x /app/entrypoint.sh
RUN mkdir -p /app/backend/staticfiles && chmod -R 755 /app/backend/staticfiles
>>>>>>> 3281c1d (production)

CMD ["gunicorn", "poligon_it.wsgi:application", "--bind", "0.0.0.0:8000"]
