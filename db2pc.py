from database import *
import pandas as pd

from sentence_transformers import SentenceTransformer

database_url = "sqlite:///jlm.db"

engine, Session = init_db_stuff(database_url)

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

df = pd.read_sql("Select * from movies", engine)
df["combined_text"] = df["title"] + ": " + df["overview"].fillna('') + " -  " + df["tagline"].fillna('') + " Genres:-  " + df["genres"].fillna('')

print(len(df["combined_text"].tolist()))

