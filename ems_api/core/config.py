from pymongo import MongoClient
from redis import Redis
import os



##
PASSWORD = os.getenv('REDIS_PASS')
HOST = str(os.getenv('REDIS_HOST'))
PORT = int(os.getenv('REDIS_PORT'))
DB = int(os.getenv('REDIS_DB'))

MDB_HOST = str(os.getenv('MDB_HOST'))
MDB_PORT = int(os.getenv('MDB_PORT'))
MDB_NAME = str(os.getenv('MDB_NAME'))
MDB_COLL = str(os.getenv('MDB_COLL'))


def redis_client():
    return Redis(HOST, PORT, DB, PASSWORD)

def mongo_db():
    '''
    Returns a specific MongoDB collection client specified in .env.
    '''
    client = MongoClient(f'mongodb://{MDB_HOST}:{MDB_PORT}/')
    db = client[MDB_NAME]
    data = db[MDB_COLL]
    return data
