##
from dotenv import load_dotenv
from celery import Celery
import os



load_dotenv()

test_mode = os.getenv('TEST_MODE').lower() in ('true')
redis_addr = str(os.getenv('REDIS_HOST'))
redis_pass = str(os.getenv('REDIS_PASS'))
redis_port = int(os.getenv('REDIS_PORT'))
db = int(os.getenv('REDIS_DB'))
username = str(os.getenv('RMQ_USERNAME'))
password = str(os.getenv('RMQ_PASSWORD'))
address = str(os.getenv('RMQ_ADDRESS'))
port = int(os.getenv('RMQ_PORT'))

broker=f'amqp://{username}:{password}@{address}:{port}//',
backend=f'redis://:{redis_pass}@{redis_addr}:{redis_port}/{db}'

if test_mode:
    broker=f'amqp://guest@{address}//',
    backend=f'redis://{redis_addr}'

app = Celery(
    'ems_api',
    broker=broker,
    backend=backend
    )

app.autodiscover_tasks(['ems_api.tasks'])
