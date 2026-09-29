from typing import Any, Dict

from fastapi import FastAPI
from database import supabase
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import os
import base64
from groq import Groq

app = FastAPI(
    title="CivicAlert AI",
    description="AI-powered community issue reporting platform",
    version="1.0.0",
)
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://civic-alert-ai-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    return {
        "status": "success",
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Photo received successfully"
    }

@app.post("/analyze-image")
def analyze_image(image_url: str):
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Analyze this civic issue image.

Return JSON with:
- issue
- category
- severity
- explanation

Category must be one of:
road, garbage, water, electricity, streetlight, drainage, other

Severity must be:
low, medium, high
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_completion_tokens=500,
    )

    return {
        "status": "success",
        "analysis": response.choices[0].message.content
    }




    
        
        
    



