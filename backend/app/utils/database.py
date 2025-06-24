import os
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError


DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


print("DB_USER:", os.getenv("DB_USER"))
print("DATABASE_URL:", DATABASE_URL)

for _ in range(10):
    try:
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,          
            )
        else:
            engine = create_engine(DATABASE_URL)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        Base = declarative_base()
        break
    except OperationalError:
        print("Database not ready yet, waiting...")
        time.sleep(1)

