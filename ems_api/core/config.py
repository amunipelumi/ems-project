##
from pymongo import MongoClient
from redis import Redis
import os



PASSWORD = os.getenv('REDIS_PASS')
HOST = str(os.getenv('REDIS_HOST'))
PORT = int(os.getenv('REDIS_PORT'))
DB = int(os.getenv('REDIS_DB'))

MDB_HOST = str(os.getenv('MDB_HOST'))
MDB_PORT = int(os.getenv('MDB_PORT'))

def redis_client():
    client = Redis(HOST, PORT, DB, PASSWORD)
    try:
        yield client
    finally:
        client.close()

def mongo_client():
    client = MongoClient(f'mongodb://{MDB_HOST}:{MDB_PORT}/')
    try:
        yield client
    finally:
        client.close()
