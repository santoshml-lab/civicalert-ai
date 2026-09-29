from fastapi import FastAPI

app = FastAPI(
    title="CivicAlert AI",
    description="AI-powered community issue reporting platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "CivicAlert AI API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CivicAlert AI",
    }
