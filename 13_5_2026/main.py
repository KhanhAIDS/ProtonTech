import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from simple_chatbot import SimpleChatbot
from fastapi.responses import RedirectResponse



app = FastAPI(
    title="LLM Chatbot REST API", 
    description="A complete FastAPI wrapper for an AI Chatbot with memory and summarization."
)

@app.get("/")
async def root():
    # Automatically redirect users to the Swagger UI docs
    return RedirectResponse(url="/docs")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# This dictionary stores memory for different users.
active_sessions = {}



class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None

class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str
    key_points: list[str]



# Requirement: Health Check
@app.get("/health")
async def health_check():
    """Checks if the server is running."""
    return {"status": "ok", "message": "Server is up and running!"}

# Requirement: Stateless Chat (No Memory)
@app.post("/chat", response_model=ChatResponse)
async def stateless_chat(request: ChatRequest):
    """Answers a single question and forgets it immediately."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.message}]
        )
        return ChatResponse(reply=response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Requirement: Stateful Chat (With Memory/Session)
@app.post("/chat/{session_id}", response_model=ChatResponse)
async def stateful_chat(session_id: str, request: ChatRequest):
    """Chats with a user and remembers their previous messages based on their session ID."""
    
    # 1. Check if this user already has an active chatbot brain. If not, create one.
    if session_id not in active_sessions:
        active_sessions[session_id] = SimpleChatbot()
        print(f"[System] Created new session memory for user: {session_id}")
    
    # 2. Retrieve their specific chatbot
    user_bot = active_sessions[session_id]
    
    # 3. Talk to the bot (the bot internally handles the history array)
    try:
        reply_text = user_bot.chat(request.message)
        return ChatResponse(reply=reply_text, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Requirement: Summarization (Strict JSON Output)
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """Takes a long text and forces the LLM to return a strict JSON summary."""
    
    # Explicitly tell the AI to output JSON with the exact keys
    system_prompt = """
    You are an expert summarizer. You must output your response in strict JSON format.
    The JSON must contain exactly two keys:
    1. 'summary': A short paragraph summarizing the text.
    2. 'key_points': A list of strings highlighting the main ideas.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" }, # This is the flag for OpenAI
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text}
            ]
        )
        
        # Parse it into a real Python dictionary.
        result_dict = json.loads(response.choices[0].message.content)
        
        # Pydantic validates it and sends it back to the user
        return SummarizeResponse(**result_dict)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))