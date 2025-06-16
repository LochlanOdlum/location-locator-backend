import os
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")

for _ in range(10):
    try:
        engine = create_engine(DATABASE_URL)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        Base = declarative_base()
        break
    except OperationalError:
        print("Database not ready yet, waiting...")
        time.sleep(1)

