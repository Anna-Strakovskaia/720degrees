from pydantic import BaseModel
from pydantic.schema import datetime


class MeasurementValues(BaseModel):
    sensor_id: int
    type: str
    date: datetime
    value: float

    class Config:
        orm_mode = True

