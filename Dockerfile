FROM python:3.9-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


WORKDIR /app
COPY . /app/


RUN pip install -r requirements.txt


CMD ["gunicorn", "poligon_it.wsgi:application", "--bind", "0.0.0.0:8000"]
