FROM python:3.11


WORKDIR /app/poligon_it

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

RUN apt-get update && apt-get install -y postgresql-client


COPY requirements.txt /app/requirements.txt


RUN pip install --upgrade pip setuptools wheel


RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app


RUN chmod +x /app/entrypoint.sh


EXPOSE 8000


ENTRYPOINT ["/app/entrypoint.sh"]
