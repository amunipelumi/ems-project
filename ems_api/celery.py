##
from dotenv import load_dotenv
from celery import Celery
import os



load_dotenv()

redis_addr = str(os.getenv('REDIS_HOST'))
redis_pass = str(os.getenv('REDIS_PASS'))
redis_port = int(os.getenv('REDIS_PORT'))
db = int(os.getenv('REDIS_DB'))
username = str(os.getenv('RMQ_USERNAME'))
password = str(os.getenv('RMQ_PASSWORD'))
address = str(os.getenv('RMQ_ADDRESS'))
port = int(os.getenv('RMQ_PORT'))


app = Celery(
    'ems_api',
    broker=f'amqp://{username}:{password}@{address}:{port}//',
    backend=f'redis://:{redis_pass}@{redis_addr}:{redis_port}/{db}'
    )

app.autodiscover_tasks(['ems_api.tasks'])
