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

@app.get("/groq-test")
def groq_test():
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: CivicAlert Groq connection successful"
            }
        ],
        max_completion_tokens=50,
        reasoning_effort="none",
    )

    return {
        "status": "success",
        "message": response.choices[0].message.content
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

Return ONLY valid JSON in exactly this format:

{
  "issue": "short description of the issue",
  "category": "road",
  "severity": "high",
  "explanation": "short explanation"
}

Allowed categories:
road, garbage, water, electricity, streetlight, drainage, other

Allowed severity:
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
        max_completion_tokens=300,
        reasoning_effort="none",
    )

    return {
        "status": "success",
        "analysis": response.choices[0].message.content
    }





    



        




    
        
        
    



