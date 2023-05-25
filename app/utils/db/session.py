from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


def get_session():
    # Определение пути к файлу базы данных
    database_uri = f"sqlite:///{os.path.dirname(__file__)}/../diseases.db"
    # Создание экземпляра движка SQLAlchemy
    engine = create_engine(database_uri)
    # Создание фабрики сессий SQLAlchemy
    session = sessionmaker(bind=engine)
    # Возвращение новой сессии
    return session()
