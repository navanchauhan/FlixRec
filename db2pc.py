import os
import pinecone

from database import *
import pandas as pd

from sentence_transformers import SentenceTransformer

from tqdm import tqdm

database_url = "sqlite:///jlm.db"
engine, Session = init_db_stuff(database_url)

PINECONE_KEY = os.getenv("PINECONE_API_DEFAULT")
pinecone.init(api_key=PINECONE_KEY, environment="us-west1-gcp")
index = pinecone.Index("movies")

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

batch_size = 32

df = pd.read_sql("Select * from movies", engine)
df["combined_text"] = df["title"] + ": " + df["overview"].fillna('') + " -  " + df["tagline"].fillna('') + " Genres:-  " + df["genres"].fillna('')

print(len(df["combined_text"].tolist()))

for x in tqdm(range(0,len(df),batch_size)):
	to_send = []
	trakt_ids = df["trakt_id"][x:x+batch_size].tolist()
	sentences = df["combined_text"][x:x+batch_size].tolist()
	embeddings = model.encode(sentences)
	for idx, value in enumerate(trakt_ids):
		to_send.append(
			{
				value: embeddings[idx].tolist()
			})
            
	print(to_send)
	index.upsert(to_send)
