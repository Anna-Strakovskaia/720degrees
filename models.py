from sqlalchemy import Column, DateTime, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MeasurementValues(Base):
    __tablename__ = 'measurement_values'
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer)
    type = Column(String)
    date = Column(DateTime(timezone=False))
    value = Column(Float)
