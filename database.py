from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///todo.db")

# Render sets DATABASE_URL with 'postgres://' but SQLAlchemy needs 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)
# Creates an engine in which the databases will be stored

SessionLocal = sessionmaker(bind=engine) #This creates a 'factory' for sessions 

def create_db():
    Base.metadata.create_all(engine)
    #Creates the databases of the Task and User classes and transfers them into todo.db

if __name__ == "__main__":
    create_db()