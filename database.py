import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, PickleType
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# database_url = "sqlite:///jlm.db"

meta = MetaData()

movies_table = Table(
    "movies",
    meta,
    Column("trakt_id", Integer, primary_key=True, autoincrement=False),
    Column("title", String),
    Column("overview", String),
    Column("genres", String),
    Column("year", Integer),
    Column("released", String),
    Column("runtime", Integer),
    Column("country", String),
    Column("language", String),
    Column("rating", Integer),
    Column("votes", Integer),
    Column("comment_count", Integer),
    Column("tagline", String),
    Column("embeddings", PickleType),
)


def init_db_stuff(database_url: str):
    engine = create_engine(database_url)
    meta.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session


"""
    movie = {
        "title": movie["movie"]["title"],
        "overview": movie["movie"]["overview"],
        "genres": movie["movie"]["genres"],
        "language": movie["movie"]["language"],
        "year": movie["movie"]["year"],
        "trakt_id": movie["movie"]["ids"]["trakt"],
        "released": movie["movie"]["released"],
        "runtime": movie["movie"]["runtime"],
        "country": movie["movie"]["country"]
    }
"""
