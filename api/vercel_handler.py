# Vercel serverless function handler for FastAPI
# Inline version - all FastAPI code is here to avoid import issues

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()

# Create FastAPI app
app = FastAPI()

# CORS configuration - allow public access
restrict_cors = os.getenv("RESTRICT_CORS", "false").lower() == "true"

if restrict_cors:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
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

# Create the handler for Vercel - this is what Vercel will call
handler = Mangum(app, lifespan="off")
