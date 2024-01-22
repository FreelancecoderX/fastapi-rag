from fastapi import FastAPI
from starlette.config import Config

config = Config(".env")

ENVIRONMENT = Config("ENVIRONMENT")
SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_configs = {"title": "RAG API"}

if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)