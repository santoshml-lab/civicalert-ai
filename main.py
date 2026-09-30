from typing import Any, Dict

from fastapi import FastAPI
from database import supabase
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import os
import base64
from groq import Groq
import json
from uuid import uuid4

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
    file_bytes = await file.read()

    file_extension = (
        file.filename.split(".")[-1]
        if "." in file.filename
        else "jpg"
    )

    file_path = f"civic-issues/{uuid4()}.{file_extension}"

    supabase.storage.from_("Warior").upload(
        file_path,
        file_bytes,
        {
            "content-type": file.content_type or "image/jpeg",
            "upsert": "false",
        },
    )

    public_url = (
        supabase.storage
        .from_("Warior")
        .get_public_url(file_path)
    )

    return {
        "status": "success",
        "filename": file.filename,
        "content_type": file.content_type,
        "storage_path": file_path,
        "image_url": public_url,
        "message": "Photo uploaded to Supabase Storage successfully",
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
def analyze_image(
    image_url: str,
    location: str = "Location not provided"
):
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

Return ONLY valid JSON:

{
  "issue": "short description",
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

    analysis_text = response.choices[0].message.content

    analysis = json.loads(analysis_text)

    issue_data = {
        "title": analysis["issue"],
        "description": analysis["explanation"],
        "category": analysis["category"],
        "severity": analysis["severity"],
        "location": location,
        "status": "pending",
        "image_url": image_url,
        "ai_explanation": analysis["explanation"],
    }

    db_response = (
        supabase
        .table("issues")
        .insert(issue_data)
        .execute()
    )

    return {
        "status": "success",
        "analysis": analysis,
        "issue": db_response.data,
    }

@app.patch("/issues/{issue_id}/status")
def update_issue_status(issue_id: int, status: str):

    allowed_statuses = [
        "pending",
        "in progress",
        "resolved"
    ]

    if status.lower() not in allowed_statuses:
        return {
            "status": "error",
            "message": "Invalid status. Use: pending, in progress, resolved"
        }

    response = (
        supabase
        .table("issues")
        .update({
            "status": status.lower()
        })
        .eq("id", issue_id)
        .execute()
    )

    return {
        "status": "success",
        "message": "Issue status updated successfully",
        "issue": response.data
    }

# ==========================================
# GENERATE CIVIC COMPLAINT
# ==========================================

@app.post("/generate-complaint")
def generate_complaint(
    issue: str,
    category: str,
    severity: str,
    location: str,
    explanation: str,
):
    try:
        prompt = f"""
Write a short professional civic complaint.

Issue: {issue}
Category: {category}
Severity: {severity}
Location: {location}
Explanation: {explanation}

Return ONLY valid JSON in exactly this format:

{{
  "subject": "short complaint subject",
  "complaint": "one short professional paragraph"
}}

Requirements:
- Mention the issue.
- Mention the location.
- Explain why attention is needed.
- Politely request appropriate action.
- Do not invent facts.
- Keep the complaint concise.
"""

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_object"
            },
            max_completion_tokens=800,
        )

        complaint_text = (
            response.choices[0].message.content
        )

        complaint = json.loads(
            complaint_text
        )

        return {
            "status": "success",
            "complaint": complaint,
        }

    except Exception as error:
        print(
            "Complaint generation error:",
            error
        )

        return {
            "status": "error",
            "message": "Unable to generate complaint.",
            "details": str(error),
        }






    



        





    



        




    
        
        
    



