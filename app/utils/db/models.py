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
    diseases_risks = relationship("DiseaseRisk", back_populates="disease")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    causes = Column(String)
    consequences = Column(String)

    diseases_risks = relationship("DiseaseRisk", back_populates="risk")


class DiseaseRisk(Base):
    __tablename__ = "diseases_risks"

    id = Column(Integer, primary_key=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    risk_id = Column(Integer, ForeignKey("risks.id"))

    disease = relationship("Disease", back_populates="diseases_risks")
    risk = relationship("Risk", back_populates="diseases_risks")
