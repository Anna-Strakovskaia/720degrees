## Set up the app

To set up conda environment:

> conda env create -f environment.yml
> conda activate 720degrees

To create database and set up tables run:

> python3 dbcreate.py
> alembic revision --autogenerate -m "New Migration"
> alembic upgrade head

Run tests:

> python3 -m unittest test_main.py

Run app:

>  uvicorn main:app --reload

Examples of requests:

>  http --json GET http://127.0.0.1:8000/measurement_values/
> 
>  http --json GET http://127.0.0.1:8000/measurement_values/1
> 
>  http --json POST http://127.0.0.1:8000/measurement_values/ sensor_id=100 type='degrees' date='2008-09-15T13:31:00' value=790
> 
>  http --json DELETE http://127.0.0.1:8000/measurement_value/1
> 
>  http --json GET "http://127.0.0.1:8000/aggregations/?agg_time=hour&type=degrees&sensor_id=100"