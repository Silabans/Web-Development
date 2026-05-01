from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine("sqlite:///todo.db", echo=True)
# Creates an engine (an sql file - todo.db) in which the databases will be stored

SessionLocal = sessionmaker(bind=engine) #This creates a 'factory' for sessions 

def create_db():
    Base.metadata.create_all(engine)
    #Creates the databases of the Task and User classes and transfers them into todo.db

if __name__ == "__main__":
    create_db()