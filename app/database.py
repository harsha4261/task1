import asyncio
import os
import re

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from .models import Base

load_dotenv()

DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or "postgresql://neondb_owner:npg_3ugC1XJMWqKb@ep-broad-surf-apdvi5zu-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
)
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
