""" Database setup base module """
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base

APP_DATABASE_URL = "sqlite:///app_data.db"
TEST_DATABASE_URL = "sqlite:///test_data.db"

engine = create_engine(APP_DATABASE_URL, connect_args={"check_same_thread": False})

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()
