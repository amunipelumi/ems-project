# Python
import os
from dotenv import load_dotenv
from os.path import abspath, dirname, join

# Program
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base



PROJECT_DIR = dirname(dirname(abspath(__file__)))
load_dotenv(join(PROJECT_DIR, '.env'))


DB_USERNAME = os.getenv('DB_USERNAME')
DB_HOSTNAME = os.getenv('DB_HOSTNAME')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DATABASE_URL = (f'postgresql://{DB_USERNAME}:{DB_PASS}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}')


Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()