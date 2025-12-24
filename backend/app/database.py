from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import load_config
import pymysql

Base = declarative_base

def get_local_db_url():
    conf = load_config()
    # Default to localhost if not set
    host = conf.get('local_host', 'localhost')
    user = conf.get('local_user', 'sa')
    password = conf.get('local_pass', '')
    db = conf.get('local_db_name', 'nhso_db')
    port = conf.get('local_port', '3306')
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

def get_local_session():
    engine = create_engine(get_local_db_url())
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()

def get_source_connection():
    """Connection for Source HOSxP (Read-only logic)"""
    conf = load_config()
    return pymysql.connect(
        host = conf.get('source_host'),
        user = conf.get('source_user'),
        password = conf.get('source_pass'),
        db = conf.get('source_db_name'),
        port = int (conf.get('source_port', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )