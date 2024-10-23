##
from pymongo import MongoClient
from redis import Redis
import os


TEST_MODE = os.getenv('TEST_MODE').lower() in ('true')

PASSWORD = os.getenv('REDIS_PASS')
HOST = str(os.getenv('REDIS_HOST'))
PORT = int(os.getenv('REDIS_PORT'))
DB = int(os.getenv('REDIS_DB'))

MDB_USER = str(os.getenv('MONGO_INITDB_ROOT_USERNAME'))
MDB_PASS = str(os.getenv('MONGO_INITDB_ROOT_PASSWORD'))
MDB_HOST = str(os.getenv('MDB_HOST'))
MDB_PORT = int(os.getenv('MDB_PORT'))

def redis_client():
    client = Redis(HOST, PORT, DB, PASSWORD)
    if TEST_MODE:
        client = Redis(HOST, PORT)
    try:
        yield client
    finally:
        client.close()

def mongo_client():
    if not TEST_MODE:
        client = MongoClient(
            f'mongodb://{MDB_USER}:{MDB_PASS}@{MDB_HOST}:{MDB_PORT}/'
            )
    else:
        client = MongoClient(f'mongodb://{MDB_HOST}:{MDB_PORT}/')
    try:
        yield client
    finally:
        client.close()
