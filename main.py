from typing import Any, Dict

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


@app.post("/issues")
def create_issue(issue: Dict[str, Any]):
    return {
        "status": "success",
        "message": "Issue received successfully",
        "issue": issue,
    }


@app.get("/issues")
def get_issues():
    return {
        "status": "success",
        "issues": [],
    }
