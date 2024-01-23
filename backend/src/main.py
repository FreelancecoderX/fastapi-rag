from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from chat import route as chat_route
from config import settings

SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_configs = {"title": "RAG API"}

if settings.ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)


@app.get("/", tags=["root"])
def root():
    return RedirectResponse("/docs")


app.include_router(chat_route.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5049)

# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiterDependency

# limiter = RateLimiterDependency(
#     rate="10/minute",
#     key="ip",
#     redis_url="redis://localhost:6379/0"
# )


# FastAPILimiter(app=app, dependency=limiter)
