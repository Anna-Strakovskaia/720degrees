from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

engine = create_engine("postgresql://localhost/720degrees")

# uncomment to drop the database to recreate
# drop_database(engine.url)

if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))