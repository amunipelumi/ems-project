from celery import Celery
import os



redis_addr = os.getenv('REDIS_HOST')
redis_pass = os.getenv('REDIS_PASS')
redis_port = int(os.getenv('REDIS_PORT'))
db = int(os.getenv('REDIS_DB'))
username = os.getenv('RMQ_USERNAME')
password = os.getenv('RMQ_PASSWORD')
address = os.getenv('RMQ_ADDRESS')
port = int(os.getenv('RMQ_PORT'))

app = Celery(
    'ems_tasks',
    broker=f'amqp://{username}:{password}@{address}:{port}//',
    backend=f'redis://:{redis_pass}@{redis_addr}:{redis_port}/{db}',
    )
