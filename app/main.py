from fastapi import FastAPI
from app import routes

app = FastAPI(title="YouTube Transcript API")

# include routes
app.include_router(routes.router)

@app.get("/healthz")
def health_check():
    return "API is running fine! Go to /docs for API documentation."
