"""
FastAPI server for Startup Evaluation Multi-Agent System
Minimal working base for backend integration
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


import asyncio

from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import Content, Part


from workflow.master.agent import root_agent


app = FastAPI(
    title="Startup Evaluation API",
    description="Multi-agent system for startup pitch analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploaded")
UPLOAD_DIR.mkdir(exist_ok=True)


session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = Runner(agent=root_agent, app_name="startup-eval", session_service=session_service, artifact_service=artifact_service)



class HealthResponse(BaseModel):
    status: str
    message: str
    version: str = "1.0.0"

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="ok",
        message="Startup Evaluation Multi-Agent System API"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Service is running properly"
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Allowed types: PDF, DOC, DOCX, TXT"
        )
    file_id = str(uuid.uuid4())
    unique_filename = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return {
        "status": "success",
        "file_id": file_id,
        "filename": unique_filename,
        "original_name": file.filename,
        "size": len(content),
        "content_type": file.content_type,
        "message": "File uploaded successfully"
    }

@app.post("/process")
async def process(request: Request):
    """
    Streams ADK agent events/results back to frontend as server-sent events.
    Expects payload JSON with 'query' or file info.
    """
    import asyncio
    import json
    from datetime import datetime

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # Support both file-based and direct text queries
    file_name = payload.get("fileName") or payload.get("filename") or payload.get("file_name")
    user_query = payload.get("query") or file_name or "No query provided"

    # Use session_id and user_id for stateful context - demo uses UUID
    session_id = payload.get("session_id", str(uuid.uuid4()))
    user_id = payload.get("user_id", "anonymous")

    async def event_stream():
        def sse(data: dict) -> bytes:
            return f"data: {json.dumps(data)}\n\n".encode("utf-8")

        # ADK session and state management
        session = await session_service.create_session(
            app_name="startup-eval", user_id=user_id, session_id=session_id
        )
        session.state["query"] = user_query

        # Bridge runner.run (may be a sync generator) to async using a queue
        queue: asyncio.Queue[object] = asyncio.Queue()

        def run_sync():
            try:
                for event in runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=Content(parts=[Part(text=user_query)])
                ):
                    queue.put_nowait(("event", event))
                queue.put_nowait(("done", None))
            except Exception as e:
                queue.put_nowait(("error", e))

        loop = asyncio.get_event_loop()
        # Run the sync runner in a thread
        fut = loop.run_in_executor(None, run_sync)

        while True:
            item_type, payload = await queue.get()
            if item_type == "event":
                event = payload
                try:
                    is_final = getattr(event, "is_final_response", lambda: False)()
                    event_type = "final" if is_final else "progress"
                    yield sse({
                        "type": event_type,
                        "content": getattr(event.content.parts[0], "text", str(event.content)),
                        "timestamp": datetime.utcnow().isoformat(),
                        "file": file_name if is_final else None,
                    })
                    # IMPORTANT: Do NOT break here; let the runner finish!
                except Exception as e:
                    yield sse({"type": "error", "content": f"Event handling error: {e}"})
            elif item_type == "error":
                yield sse({"type": "error", "content": str(payload)})
                break
            elif item_type == "done":
                break

        # Ensure background future completes
        try:
            await fut
        except Exception:
            pass

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
