from fastapi import FastAPI, Request, Depends
from app import routes
from app.limiting.deps import rate_limit_dependency

app = FastAPI(title="YouTube Transcript API")

# Middleware to attach rate-limit headers
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    hdrs = getattr(request.state, "rate_limit_headers", None)
    if hdrs:
        for k, v in hdrs.items():
            response.headers[k] = v
    return response

# include routes
app.include_router(routes.router)

@app.get("/healthz")
def health_check():
    return "API is running fine! Go to /docs for API documentation."

@app.get("/", dependencies=[Depends(rate_limit_dependency())])
def root():
    return {"message": "Welcome to the YouTube Transcript API! Visit /docs for API documentation."}