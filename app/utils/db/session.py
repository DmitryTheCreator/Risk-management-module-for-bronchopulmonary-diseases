from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


def get_session():
    database_uri = f"sqlite:///{os.path.dirname(__file__)}/../diseases.db"
    engine = create_engine(database_uri)
    session = sessionmaker(bind=engine)
    return session()
