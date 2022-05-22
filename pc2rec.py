from database import *
from sqlalchemy.sql import select

database_url = "sqlite:///jlm.db"

engine, Session = init_db_stuff(database_url)

from sqlalchemy import func

movie_name = "Forrest Gump"

with engine.connect() as conn:
	movie_deets = select(movies_table).filter(func.lower(movies_table.columns.title)==func.lower(movie_name))
	result = conn.execute(movie_deets)
	for row in result:
		print(row)