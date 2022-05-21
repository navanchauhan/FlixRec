import requests
import os
from database import *
from tqdm import tqdm

from datetime import datetime

import time

trakt_id = os.getenv("TRAKT_ID")
trakt_se = os.getenv("TRAKT_SE")

max_requests = 5000 # How many requests do you want to make 
req_count = 0

years = "1900-2021"
page = 1
extended = "full" # Required to get additional information 
limit = "10" # No of entires per request
languages = "en" # Limit to particular language

api_base = "https://api.trakt.tv"
database_url = "sqlite:///jlm.db"

headers = {
	"Content-Type": "application/json",
	"trakt-api-version": "2",
	"trakt-api-key": trakt_id
}

params = {
	"query": "",
	"years": years,
	"page": page,
	"extended": extended,
	"limit": limit,
	"languages": languages
}


def create_movie_dict(movie: dict):
	movie = {
		"title": movie["movie"]["title"],
		"overview": movie["movie"]["overview"],
		"genres": movie["movie"]["genres"],
		"language": movie["movie"]["language"],
		"year": int(movie["movie"]["year"]),
		"trakt_id": movie["movie"]["ids"]["trakt"],
		"released": movie["movie"]["released"],
		"runtime": int(movie["movie"]["runtime"]),
		"country": movie["movie"]["country"],
		"rating": int(movie["movie"]["rating"]),
		"votes": int(movie["movie"]["votes"]),
		"comment_count": int(movie["movie"]["comment_count"]),
		"tagline": movie["movie"]["tagline"]
	}
	return movie



params["limit"] = 1
res = requests.get(f"{api_base}/search/movie",headers=headers,params=params)
total_items = res.headers["x-pagination-item-count"]

print(f"There are {total_items} movies")
print(f"Started from page {page}")

"""
movies = []
params["limit"] = limit
res = requests.get(f"{api_base}/search/movie",headers=headers,params=params)

if res.status_code == 200:
	for movie in res.json():
		movies.append(create_movie_dict(movie))
		print(create_movie_dict(movie)["title"])
"""
engine, Session = init_db_stuff(database_url)

start_time = datetime.now()

for page in tqdm(range(2990,max_requests+10)):
	if req_count == 999:
		seconds_to_sleep = 300 - (datetime.now() - start_time).seconds
		if seconds_to_sleep < 1:
			seconds_to_sleep = 100
		print(f"Sleeping {seconds_to_sleep}s")
		# Need to respect their rate limitting
		time.sleep(seconds_to_sleep)
		start_time = datetime.now()
		req_count = 0

	params["page"] = page
	params["limit"] = int(int(total_items)/max_requests)
	movies = []
	res = requests.get(f"{api_base}/search/movie",headers=headers,params=params)

	if res.status_code == 500:
		break
	elif res.status_code == 200:
		None
	else:
		print(f"OwO Code {res.status_code}")

	for movie in res.json():
		movies.append(create_movie_dict(movie))

	with engine.connect() as conn:
		for movie in movies:
			with conn.begin() as trans:
				stmt = insert(movies_table).values(
					trakt_id=movie["trakt_id"], title=movie["title"], genres=" ".join(movie["genres"]),
					language=movie["language"], year=movie["year"], released=movie["released"],
					runtime=movie["runtime"], country=movie["country"], overview=movie["overview"],
					rating=movie["rating"], votes=movie["votes"], comment_count=movie["comment_count"],
					tagline=movie["tagline"])
				try:
					result = conn.execute(stmt)
					trans.commit()
				except IntegrityError:
					trans.rollback()
	req_count += 1
