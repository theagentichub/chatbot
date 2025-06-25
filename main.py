from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import uuid, os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    ],
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "max_output_tokens": 1024,
    }
)

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
session_memory = {}

# Pydantic models
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

# Root route for health check
@app.get("/")
async def root():
    return "Its working! Chatbot API is running."

# Helper to build prompt from history
def build_prompt(session_id: str, user_input: str) -> str:
    try:
        with open("prompt_template.txt", "r") as f:
            template = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Prompt template not found")

    history = session_memory.get(session_id, [])
    history_text = "\n".join(history[-10:])
    return template.format(history=history_text, user_input=user_input)

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.session_id not in session_memory:
        session_memory[req.session_id] = []

    session_memory[req.session_id].append(f"Customer: {req.message}")
    prompt = build_prompt(req.session_id, req.message)

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

    session_memory[req.session_id].append(f"Chatbot: {reply}")
    return ChatResponse(response=reply)

# Clear session memory
@app.post("/end_session/{session_id}")
async def end_session(session_id: str):
    if session_id in session_memory:
        del session_memory[session_id]
    return {"message": "Session ended and memory cleared."}
