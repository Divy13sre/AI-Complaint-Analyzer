from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
import os
import json
import time


# Load environment variables from .env
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)


# Request model
class ComplaintRequest(BaseModel):
    complaint: str


# Create FastAPI app
app = FastAPI()

# Store complaint history
complaint_history = []


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "AI Complaint Analyzer is running!"
    }


# Analyze complaint using Gemini AI
@app.post("/analyze-complaint")
def analyze_complaint(data: ComplaintRequest):

    complaint = data.complaint

    # Prompt for Gemini AI
    prompt = f"""
You are a customer complaint analysis assistant.

Analyze the following customer complaint:

"{complaint}"

Return ONLY valid JSON in this exact format:

{{
    "category": "category name",
    "priority": "High, Medium, or Low",
    "summary": "short summary of the complaint"
}}

Choose the most appropriate category.

Possible categories:
- Payment Issue
- Delivery Issue
- Account Issue
- Refund Issue
- Product Quality Issue
- Technical Issue
- General Complaint

Priority rules:
- High: serious payment, refund, damaged product, or critical issue
- Medium: delivery, account, or normal technical issue
- Low: general or minor issue
"""

    try:

        # Send complaint to Gemini with retry
        response = None

        for attempt in range(3):
            try:

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

                break

            except Exception as error:

                print(
                    f"Gemini attempt {attempt + 1} failed:",
                    error
                )

                if attempt < 2:
                    time.sleep(3)
                else:
                    raise error

        # Get AI response
        ai_text = response.text.strip()

        # Remove markdown code fences if Gemini returns them
        if ai_text.startswith("```"):
            ai_text = ai_text.replace("```json", "")
            ai_text = ai_text.replace("```", "")
            ai_text = ai_text.strip()

        # Convert JSON text into Python dictionary
        result = json.loads(ai_text)

        # Get AI-generated values
        category = result["category"]
        priority = result["priority"]
        summary = result["summary"]

    except Exception as error:

        # Print actual error in terminal
        print("Gemini error:", error)

        return {
            "complaint": complaint,
            "category": "AI Error",
            "priority": "Low",
            "summary": f"AI analysis failed: {str(error)}"
        }

    # Store successful complaint analysis
    complaint_history.append({
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "summary": summary
    })

    # Return result to frontend
    return {
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "summary": summary
    }


# Get complaint history
@app.get("/history")
def get_history():

    return {
        "history": complaint_history
    }


# Get dashboard statistics
@app.get("/dashboard")
def get_dashboard():

    total_complaints = len(complaint_history)

    high_priority = 0
    medium_priority = 0
    low_priority = 0

    category_count = {}

    for item in complaint_history:

        # Count priority
        if item["priority"] == "High":
            high_priority += 1

        elif item["priority"] == "Medium":
            medium_priority += 1

        elif item["priority"] == "Low":
            low_priority += 1

        # Count categories
        category = item["category"]

        if category in category_count:
            category_count[category] += 1
        else:
            category_count[category] = 1

    return {
        "total_complaints": total_complaints,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "category_count": category_count
    }