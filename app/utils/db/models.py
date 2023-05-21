from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    parent_id = Column(Integer, ForeignKey("diseases.id"))

    parent = relationship("Disease", remote_side=[id])
