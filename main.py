"""
FastAPI server for Startup Evaluation Multi-Agent System
Minimal working base for backend integration
"""

import asyncio
import contextlib
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content
from google.genai import types
from pydantic import BaseModel

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
        "file_path": str(file_path.resolve()),
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
    import json
    from datetime import datetime

    try:
        request_payload = await request.json()
    except Exception:
        request_payload = {}

    # Support both file-based and direct text queries
    file_name = request_payload.get("fileName") or request_payload.get("filename") or request_payload.get("file_name")
    user_query = request_payload.get("query") or file_name or "No query provided"

    # Use session_id and user_id for stateful context - demo uses UUID
    session_id = request_payload.get("session_id", str(uuid.uuid4()))
    user_id = request_payload.get("user_id", "anonymous")

    async def event_stream():
        def sse(data: dict) -> bytes:
            return f"data: {json.dumps(data)}\n\n".encode()

        # ADK session and state management
        session = await session_service.create_session(
            app_name="startup-eval", user_id=user_id, session_id=session_id
        )
        session.state["query"] = user_query

        # Determine session directory name(s) used by agents on disk
        sessions_root = Path("sessions")
        candidate1 = f"{user_id}_session_{session_id}_startup-eval"
        candidate2 = f"{user_id}_{session_id}_startup-eval"
        chosen_dir = None
        try:
            if (sessions_root / candidate1).exists():
                chosen_dir = candidate1
            elif (sessions_root / candidate2).exists():
                chosen_dir = candidate2
            else:
                # prefer candidate1 as default naming
                chosen_dir = candidate1
        except Exception:
            chosen_dir = candidate1

        # Send an initial SSE with session directory info so UI can poll exact path
        yield sse({
            "type": "session_info",
            "session_dirname": chosen_dir,
            "session_path": str((sessions_root / chosen_dir).resolve()),
        })

        # Bridge runner.run (may be a sync generator) to async using a queue
        queue: asyncio.Queue[object] = asyncio.Queue()

        def run_sync():
            try:
                # Build message parts, include file bytes if available
                parts = [types.Part(text=user_query)]

                incoming_file_path = request_payload.get("filePath") or request_payload.get("file_path")
                if incoming_file_path:
                    try:
                        p = Path(incoming_file_path)
                        if p.exists():
                            data = p.read_bytes()
                            parts.append(types.Part.from_bytes(data=data, mime_type="application/pdf"))
                    except Exception:
                        # Ignore read errors and continue without inline data
                        pass
                else:
                    # Fallback: resolve by filename in UPLOAD_DIR
                    if file_name:
                        candidate = UPLOAD_DIR / file_name
                        if candidate.exists():
                            try:
                                data = candidate.read_bytes()
                                parts.append(types.Part.from_bytes(data=data, mime_type="application/pdf"))
                            except Exception:
                                pass

                for event in runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=Content(parts=parts),
                ):
                    queue.put_nowait(("event", event))

                queue.put_nowait(("done", None))
            except Exception as e:
                queue.put_nowait(("error", e))

        loop = asyncio.get_event_loop()
        # Run the sync runner in a thread
        fut = loop.run_in_executor(None, run_sync)

        while True:
            item_type, qpayload = await queue.get()
            if item_type == "event":
                event = qpayload
                try:
                    is_final = getattr(event, "is_final_response", lambda: False)()
                    event_type = "final" if is_final else "progress"

                    # Safely extract text content from event parts. If the first available
                    # part has `.text`, use it. If it has `inline_data` (binary), summarize
                    # instead of dumping the bytes to the SSE stream.
                    content_text = None
                    try:
                        if hasattr(event, "content") and getattr(event.content, "parts", None):
                            for p in event.content.parts:
                                if getattr(p, "text", None):
                                    content_text = p.text
                                    break
                                if getattr(p, "inline_data", None):
                                    inline = p.inline_data
                                    size = len(inline.data) if getattr(inline, "data", None) else None
                                    mime = getattr(inline, "mime_type", None)
                                    content_text = f"[attached file: {size} bytes, mime={mime}]"
                                    break
                    except Exception:
                        content_text = None

                    if content_text is None:
                        # Fallback to a concise string representation
                        try:
                            content_text = str(event.content)
                        except Exception:
                            content_text = "<unserializable event content>"

                    yield sse({
                        "type": event_type,
                        "content": content_text,
                        "timestamp": datetime.utcnow().isoformat(),
                        "file": file_name if is_final else None,
                    })
                    # IMPORTANT: Do NOT break here; let the runner finish!
                except Exception as e:
                    yield sse({"type": "error", "content": f"Event handling error: {e}"})
            elif item_type == "error":
                yield sse({"type": "error", "content": str(qpayload)})
                break
            elif item_type == "done":
                break

        # Ensure background future completes
        with contextlib.suppress(Exception):
            await fut

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
