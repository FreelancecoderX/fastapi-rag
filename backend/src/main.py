from fastapi import FastAPI
from starlette.config import Config

# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiterDependency

from chat import route as chat_route

config = Config(".env")

ENVIRONMENT = Config("ENVIRONMENT")
SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_configs = {"title": "RAG API"}

if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)

app.include_router(chat_route.router)

# limiter = RateLimiterDependency(
#     rate="10/minute",
#     key="ip",
#     redis_url="redis://localhost:6379/0"
# )


# FastAPILimiter(app=app, dependency=limiter)
