import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import MeasurementValues as SchemaMeasurementValues
from models import MeasurementValues as ModelMeasurementValues

import os
from dotenv import load_dotenv

from typing import Optional
from pydantic.schema import datetime

import pandas as pd

load_dotenv('.env')

app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.post('/measurement_values/')
def measurement_value(measurement_values: SchemaMeasurementValues):
    values = ModelMeasurementValues(
        sensor_id=measurement_values.sensor_id,
        type=measurement_values.type,
        date=measurement_values.date,
        value=measurement_values.value,
    )
    db.session.add(values)
    db.session.commit()
    db.session.refresh(values)
    return {'id': values.id}


@app.delete('/measurement_values/{value_id}')
def measurement_value(value_id: int):
    # delete a record by id
    try:
        rows_amount = db.session.query(ModelMeasurementValues).filter_by(id=value_id).delete()
        if rows_amount == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        else:
            db.session.commit()
    except HTTPException:
        raise


@app.get('/measurement_values/{value_id}')
def measurement_value(value_id: int):
    # get a record by id
    data = db.session.query(ModelMeasurementValues).get(value_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return data


@app.get('/measurement_values/')
def measurement_value():
    # get all records
    data = db.session.query(ModelMeasurementValues).all()
    return data


@app.get('/aggregations/')
def calculate_statistics(
        agg_time: str,
        sensor_id: int,
        type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
):
    # requested aggregation time validation
    if agg_time == 'hour':
        resample_arg = 'H'
    elif agg_time == '5min':
        resample_arg = '5min'
    else:
        raise HTTPException(status_code=400, detail="Bad request. Time period can only be 'hour' or '5min'")

    # requested dates validation
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Bad request. The start date is later than the end date.")

    # read data
    query = db.session.query(ModelMeasurementValues)
    query = query.filter_by(sensor_id=sensor_id, type=type).statement
    data = pd.read_sql(query, db.session.bind)

    # filter data
    if start_date and end_date:
        data = data[data.date >= start_date]
        data = data[data.date <= end_date]

    # checking if requested data exists
    if len(data) == 0:
        raise HTTPException(status_code=404, detail="Requested records not found")

    # aggregate and calculate statistics
    data = data[['value', 'date']].resample(resample_arg, on='date').agg(['min', 'max', 'mean'])
    data.columns = data.columns.droplevel(0)
    data = data.reset_index()
    data = data.assign(sensor_id=sensor_id, type=type).dropna()

    # convert to json
    data = data.to_dict('records')

    return data

# to run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
