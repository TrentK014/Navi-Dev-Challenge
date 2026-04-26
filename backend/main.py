import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from chat import run_chat

app = FastAPI()

ALLOWED_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != "*" else ["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1, max_length=50)


class ChatResponse(BaseModel):
    text: str
    queries: list[str]


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    if not last_user or not last_user.content.strip():
        raise HTTPException(status_code=400, detail="Empty user message.")
    if len(last_user.content) > 4000:
        raise HTTPException(status_code=400, detail="Message too long (max 4000 chars).")
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    try:
        result = run_chat(msgs)
        return ChatResponse(**result)
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong processing that.")
