from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# 🔥 ADD THIS HERE (not inside main)
from app.db import models


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully 🚀")