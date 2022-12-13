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
