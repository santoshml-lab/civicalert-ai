from typing import Any, Dict

from fastapi import FastAPI
from database import supabase

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
    response = (
        supabase
        .table("issues")
        .insert(issue)
        .execute()
    )

    return {
        "status": "success",
        "message": "Issue saved successfully",
        "issue": response.data,
    }

@app.get("/issues")
def get_issues():
    response = (
        supabase
        .table("issues")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "status": "success",
        "issues": response.data,
    }




    
        
        
    



