import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ENDPOINT = os.getenv("DATABASE_ENDPOINT")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_ENDPOINT}/locationlocator",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()