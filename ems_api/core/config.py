from pymongo import MongoClient
from gridfs import GridFS
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


rd_client = Redis(HOST, PORT, DB, PASSWORD)
mdb_client = MongoClient(f'mongodb://{MDB_HOST}:{MDB_PORT}/')

def redis_client():
    try:
        yield rd_client
    finally:
        rd_client.close()

def mongo_client():
    try:
        yield mdb_client
    finally:
        mdb_client.close()

def mongo_coll():
    '''
    Return MongoDB collection.
    '''
    client = mongo_client()
    return client[MDB_NAME][MDB_COLL]

def doc_upload():
    '''
    Returns GridFS ready for storing documents and files in MongoDB.
    '''
    client = mongo_client()
    db = client[MDB_NAME]
    # coll = db[MDB_COLL]
    return GridFS(db)
