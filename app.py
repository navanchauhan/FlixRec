from flask import Flask, render_template, request, url_for
from database import *
import pandas as pd
from fuzzywuzzy import process, fuzz
import os
import pinecone

PINECONE_KEY = os.getenv("PINECONE_API_DEFAULT")

database_url = "sqlite:///jlm.db"

engine, Session = init_db_stuff(database_url)

df = pd.read_sql("Select * from movies", engine)
movie_titles = df["title"].tolist()

pinecone.init(api_key=PINECONE_KEY, environment="us-west1-gcp")
index = pinecone.Index("movies")

app = Flask(__name__, template_folder="./templates")


def title2trakt_id(title: str, df=df):
    # Matches Exact Title, Otherwise Returns None
    records = df[df["title"].str.lower() == title.lower()]
    if len(records) == 0:
        return 0, None
    elif len(records) == 1:
        return 1, records.trakt_id.tolist()[0]
    else:
        return 2, records.trakt_id.tolist()


def get_vector_value(trakt_id: int):
    fetch_response = index.fetch(ids=[str(trakt_id)])
    return fetch_response["vectors"][str(trakt_id)]["values"]


def query_vectors(
    vector: list,
    top_k: int = 20,
    include_values: bool = False,
    include_metada: bool = True,
):
    query_response = index.query(
        queries=[
            (vector),
        ],
        top_k=top_k,
        include_values=include_values,
        include_metadata=include_metada,
    )
    return query_response


def query2ids(query_response):
    trakt_ids = []
    for match in query_response["results"][0]["matches"]:
        trakt_ids.append(int(match["id"]))
    return trakt_ids


def get_deets_by_trakt_id(df, trakt_id: int):
    df = df[df["trakt_id"] == trakt_id]
    return {
        "title": df.title.values[0],
        "overview": df.overview.values[0],
        "runtime": int(df.runtime.values[0]),
        "year": int(df.year.values[0]),
        "trakt_id": trakt_id,
        "tagline": df.tagline.values[0],
    }


@app.route("/similar")
def get_similar_titles():
    trakt_id = request.args.get("trakt_id")
    filterin = request.args.get("filter")

    min_year = request.args.get("minYear")
    if min_year == None:
        min_year = 1900
    else:
        try:
            min_year = int(min_year)
        except TypeError:
            min_year = 1900
    max_year = request.args.get("maxYear")
    if max_year == None:
        max_year = 2021
    else:
        try:
            max_year = int(max_year)
        except TypeError:
            max_year = 2021
    minRuntime = request.args.get("minRuntime")
    if minRuntime == None:
        minRuntime = 70
    else:
        try:
            minRuntime = int(minRuntime)
        except TypeError:
            minRuntime = 70
    maxRuntime = request.args.get("maxRuntime")
    if maxRuntime == None:
        maxRuntime = 220
    else:
        try:
            maxRuntime = int(maxRuntime)
        except TypeError:
            maxRuntime = 220
    vector = get_vector_value(trakt_id)
    movie_queries = query_vectors(vector, top_k=69)
    movie_ids = query2ids(movie_queries)
    results = []
    # for trakt_id in movie_ids:
    #    deets = get_deets_by_trakt_id(df, trakt_id)
    #    results.append(deets)
    max_res = 30
    cur_res = 0
    for trakt_id in movie_ids:
        if cur_res >= max_res:
            break
        deets = get_deets_by_trakt_id(df, trakt_id)
        if ((deets["year"] >= min_year) and (deets["year"] <= max_year)) and (
            (deets["runtime"] >= minRuntime) and (deets["runtime"] <= maxRuntime)
        ):
            results.append(deets)
            cur_res += 1
    return render_template("show_results.html", deets=results)


@app.route("/", methods=("GET", "POST"))
def find_similar_title():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        to_search_title = request.form["title"]
        code, values = title2trakt_id(to_search_title)
        print(f"Code {code} for {to_search_title}")
        if code == 0:
            search_results = process.extract(
                to_search_title, movie_titles, scorer=fuzz.token_sort_ratio
            )
            to_search_titles = []
            to_search_ids = []
            results = []
            for search_result in search_results:
                search_title, score = search_result
                to_search_titles.append(search_title)
            for to_search in to_search_titles:
                code, values = title2trakt_id(to_search)
                if code == 1:
                    to_search_ids.append(values)
                else:
                    for trakt_id in values:
                        to_search_ids.append(trakt_id)
            for trakt_id in to_search_ids:
                deets = get_deets_by_trakt_id(df, int(trakt_id))
                deets["trakt_id"] = trakt_id
                results.append(deets)
            return render_template("same_titles.html", deets=results)

        elif code == 1:
            vector = get_vector_value(values)
            movie_queries = query_vectors(vector)
            movie_ids = query2ids(movie_queries)
            results = []
            for trakt_id in movie_ids:
                deets = get_deets_by_trakt_id(df, trakt_id)
                results.append(deets)
            return render_template("show_results.html", deets=results)
        else:
            results = []
            for trakt_id in values:
                deets = get_deets_by_trakt_id(df, int(trakt_id))
                deets["trakt_id"] = trakt_id
                results.append(deets)
            return render_template("same_titles.html", deets=results)
