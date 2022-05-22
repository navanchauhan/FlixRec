# FlixRec

a content based movie recommendation system

## Deploy Flask App

```
poetry shell # python3 -m venv my_env && source my_env/bin/activate
poetry install
waitress-serve --port=8041 app:app
```

Don't forget to set `PINECONE_API_DEFAULT`