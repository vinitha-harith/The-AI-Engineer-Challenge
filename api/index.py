from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS configuration - allow public access
# By default, allows all origins for public access
# Set RESTRICT_CORS=true to restrict to specific origins
restrict_cors = os.getenv("RESTRICT_CORS", "false").lower() == "true"

if restrict_cors:
    # Restricted mode: only allow specific origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Add frontend URL from environment if set
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url:
        allowed_origins.append(frontend_url)
else:
    # Public mode: allow all origins (default for public access)
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if not restrict_cors else False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        user_message = request.message
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using valid OpenAI model (gpt-5 doesn't exist)
            messages=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": user_message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")
