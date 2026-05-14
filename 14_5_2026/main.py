import os
import json
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from simple_chatbot import SimpleChatbot
from fastapi.responses import RedirectResponse
from resilience import retry_with_backoff, call_with_timeout, fallback_chain, openai_circuit

app = FastAPI(
    title="LLM Chatbot REST API", 
    description="FastAPI wrapper with memory, summarization, and resilience."
)

# Day 8 Sync Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Day 9 Async Client (Required for timeout feature)
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

active_sessions = {}

# --- Schemas ---
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

class ResilientChatRequest(BaseModel):
    message: str
    simulate_delay: float = 0.0 
    simulate_error: bool = False 

class ResilientChatResponse(BaseModel):
    reply: str
    source: str = "openai"

# --- Day 8 Endpoints ---
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is up and running!"}

# --- Day 9 Resilient Endpoint ---
async def call_openai_async(message: str, simulate_delay: float, simulate_error: bool):
    if simulate_delay > 0:
        await asyncio.sleep(simulate_delay)
    if simulate_error:
        raise Exception("Simulated OpenAI Error")
        
    response = await async_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

@app.post("/chat/resilient", response_model=ResilientChatResponse)
async def resilient_chat(request: ResilientChatRequest):
    async def primary_execution():
        async def circuit_call():
            return await openai_circuit.call(
                call_openai_async, 
                request.message, 
                request.simulate_delay, 
                request.simulate_error
            )
        async def timed_call():
            return await call_with_timeout(circuit_call, timeout=3.0)
            
        return await retry_with_backoff(timed_call, max_retries=2, base_delay=1)

    try:
        reply = await fallback_chain(
            primary_func=primary_execution,
            default_response="[Cache] Hệ thống hiện đang quá tải. Vui lòng thử lại sau."
        )
        source = "cache" if "[Cache]" in reply else "openai"
        return ResilientChatResponse(reply=reply, source=source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def stateless_chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.message}]
        )
        return ChatResponse(reply=response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/{session_id}", response_model=ChatResponse)
async def stateful_chat(session_id: str, request: ChatRequest):
    if session_id not in active_sessions:
        active_sessions[session_id] = SimpleChatbot()
    
    user_bot = active_sessions[session_id]
    try:
        reply_text = user_bot.chat(request.message)
        return ChatResponse(reply=reply_text, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    system_prompt = """
    You are an expert summarizer. You must output your response in strict JSON format.
    The JSON must contain exactly two keys:
    1. 'summary': A short paragraph summarizing the text.
    2. 'key_points': A list of strings highlighting the main ideas.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text}
            ]
        )
        result_dict = json.loads(response.choices[0].message.content)
        return SummarizeResponse(**result_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))