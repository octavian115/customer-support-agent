"""
FastAPI application for the TaskFlow support agent.

Endpoints:
    POST /chat              — Customer sends a message
    GET  /pending           — Get threads waiting for human review
    POST /review            — Human approves/rejects a pending action
    GET  /threads           — List all conversation threads
    GET  /thread/{id}/messages — Get full conversation history for a thread
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from backend.graph import support_agent

app = FastAPI(title="TaskFlow Support Agent API")

# In-memory thread tracking
threads = {}

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):
    thread_id: str
    status: str  # "completed" or "pending_review"
    response: str | None = None
    interrupt_info: dict | None = None

class ReviewRequest(BaseModel):
    thread_id: str
    approved: Literal["yes", "no"]  # "yes" or "no"
    edited_response: str | None = None


@app.get("/")
def health_check():
    return {"status": "ok", "service": "TaskFlow Support Agent"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Track the thread if it's new
    if request.thread_id not in threads:
        threads[request.thread_id] = {
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }

    config = {"configurable": {"thread_id": request.thread_id}}
    state = {"messages": [HumanMessage(content=request.message)]}

    result = support_agent.invoke(state, config=config)

    # Check if the graph hit an interrupt
    snapshot = support_agent.get_state(config)

    if snapshot.tasks:
        # Graph is paused — HITL needed
        interrupt_value = snapshot.tasks[0].interrupts[0].value
        threads[request.thread_id]["status"] = "pending_review"

        return ChatResponse(
            thread_id=request.thread_id,
            status="pending_review",
            response="Let me check with my team on this. I'll get back to you shortly.",
            interrupt_info=interrupt_value,
        )

    else:
        # Graph completed normally
        threads[request.thread_id]["status"] = "active"
        last_message = result["messages"][-1].content

        return ChatResponse(
            thread_id=request.thread_id,
            status="completed",
            response=last_message,
        )

@app.get("/pending")
def get_pending():
    pending = []
    for thread_id, info in threads.items():
        if info["status"] == "pending_review":
            config = {"configurable": {"thread_id": thread_id}}
            snapshot = support_agent.get_state(config)

            if snapshot.tasks:
                interrupt_value = snapshot.tasks[0].interrupts[0].value
                pending.append({
                    "thread_id": thread_id,
                    "created_at": info["created_at"],
                    "interrupt_info": interrupt_value,
                })

    return {"pending": pending}


@app.post("/review")
def review(request: ReviewRequest):
    # Verify thread exists and is pending
    if request.thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    if threads[request.thread_id]["status"] != "pending_review":
        raise HTTPException(status_code=400, detail="Thread is not pending review")

    config = {"configurable": {"thread_id": request.thread_id}}

    # Build the resume payload
    decision = {"approved": request.approved}
    if request.edited_response:
        decision["edited_response"] = request.edited_response

    # Resume the graph
    result = support_agent.invoke(
        Command(resume=decision),
        config=config,
    )

    # Update status
    threads[request.thread_id]["status"] = "active"

    last_message = result["messages"][-1].content

    return {
        "thread_id": request.thread_id,
        "status": "completed",
        "response": last_message,
    }

@app.get("/threads")
def get_threads():
    return {"threads": [
        {
            "thread_id": thread_id,
            "status": info["status"],
            "created_at": info["created_at"],
        }
        for thread_id, info in threads.items()
    ]}


@app.get("/thread/{thread_id}/messages")
def get_thread_messages(thread_id: str):
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread not found")

    config = {"configurable": {"thread_id": thread_id}}
    snapshot = support_agent.get_state(config)

    messages = []
    for msg in snapshot.values["messages"]:
        messages.append({
            "role": msg.type,  # "human" or "ai"
            "content": msg.content,
        })

    return {"thread_id": thread_id, "messages": messages}