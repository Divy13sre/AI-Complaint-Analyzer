
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class ComplaintRequest(BaseModel):
    complaint: str


app = FastAPI()

complaint_history = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI Complaint Analyzer is running!"}


@app.post("/analyze-complaint")
def analyze_complaint(data: ComplaintRequest):

    complaint = data.complaint
    complaint_lower = complaint.lower()

    if "payment" in complaint_lower or "money" in complaint_lower:
        category = "Payment Issue"
        priority = "High"

    elif "delivery" in complaint_lower or "late" in complaint_lower:
        category = "Delivery Issue"
        priority = "Medium"

    elif "login" in complaint_lower or "password" in complaint_lower:
        category = "Account Issue"
        priority = "Medium"

    elif "refund" in complaint_lower or "return" in complaint_lower:
        category = "Refund Issue"
        priority = "High"

    elif "damaged" in complaint_lower or "broken" in complaint_lower:
        category = "Product Quality Issue"
        priority = "High"

    elif (
        "website" in complaint_lower
        or "app" in complaint_lower
        or "error" in complaint_lower
    ):
        category = "Technical Issue"
        priority = "Medium"

    else:
        category = "General Complaint"
        priority = "Low"


    # Generate summary based on category

    if category == "Payment Issue":
        summary = "The customer is facing a payment-related problem with the order."

    elif category == "Delivery Issue":
        summary = "The customer is experiencing a delay in receiving the order."

    elif category == "Account Issue":
        summary = "The customer is having difficulty accessing or managing their account."

    elif category == "Refund Issue":
        summary = "The customer is requesting assistance with a refund or return."

    elif category == "Product Quality Issue":
        summary = "The customer reported that the received product is damaged or defective."

    elif category == "Technical Issue":
        summary = "The customer is experiencing a technical problem with the application or website."

    else:
        summary = "The customer has reported a general issue requiring further investigation."


    complaint_history.append({
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "summary": summary
    })


    return {
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "summary": summary
    }


@app.get("/history")
def get_history():
    return {
        "history": complaint_history
    }


@app.get("/dashboard")
def get_dashboard():

    total_complaints = len(complaint_history)

    high_priority = 0
    medium_priority = 0
    low_priority = 0

    category_count = {}

    for item in complaint_history:

        if item["priority"] == "High":
            high_priority += 1

        elif item["priority"] == "Medium":
            medium_priority += 1

        elif item["priority"] == "Low":
            low_priority += 1

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

