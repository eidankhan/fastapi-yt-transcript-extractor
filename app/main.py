from fastapi import FastAPI, Request, Depends
from app.limiting.deps import (rate_limit_dependency, redis_rate_limit_dependency,
                               token_bucket_dependency, tiered_token_bucket_dependency)
from .database import Base, engine
from fastapi.responses import JSONResponse
from app.routes import users, transcripts


# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="YouTube Transcript API")


# Middleware to handle API keys + attach rate-limit headers
@app.middleware("http")
async def api_key_and_rate_limit_middleware(request: Request, call_next):
    """
    Middleware that:
    - Skips API key check for public routes (register, healthz, docs).
    - Requires API key for all other routes.
    - Attaches rate-limit headers set by dependencies.
    """
    public_paths = ["/","/users/register", "/users/login", "/healthz", "/docs", "/openapi.json"]

    # Allow public routes without API key
    if request.url.path not in public_paths:
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return JSONResponse(status_code=401, content={"detail": "API key required"})

    # Process request
    response = await call_next(request)

    # Attach rate limit headers if set by dependency
    hdrs = getattr(request.state, "rate_limit_headers", None)
    if hdrs:
        for k, v in hdrs.items():
            response.headers[k] = v
    return response

# include routes
app.include_router(users.router)  # 👈 user register + login
app.include_router(transcripts.router)  # 👈 transcripts

@app.get("/healthz")
def health_check():
    return "API is running fine! Go to /docs for API documentation."

@app.get("/")
def root():
    return {"message": "Welcome to the YouTube Transcript API! Visit /docs for API documentation."}