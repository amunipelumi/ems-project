from redis import Redis
import os



##
PASSWORD = os.getenv('REDIS_PASS')
HOST = str(os.getenv('REDIS_HOST'))
PORT = int(os.getenv('REDIS_PORT'))
DB = int(os.getenv('REDIS_DB'))

def redis_client():
    return Redis(HOST, PORT, DB, PASSWORD)
