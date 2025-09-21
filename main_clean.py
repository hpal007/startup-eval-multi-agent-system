"""
FastAPI server for Startup Evaluation Multi-Agent System
Minimal working base for backend integration
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
