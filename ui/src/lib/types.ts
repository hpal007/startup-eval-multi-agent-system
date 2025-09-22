// Core types for the startup evaluation system
export interface ProcessingEvent {
  type: "progress" | "agent_start" | "agent_complete" | "error" | "final";
  content: string;
  timestamp: Date;
  agentName?: string;
  metadata?: Record<string, unknown>;
}

export interface UploadedFile {
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
}

export interface ProcessingSession {
  id: string;
  userId: string;
  file: UploadedFile;
  status: "uploading" | "processing" | "completed" | "error";
  events: ProcessingEvent[];
  createdAt: Date;
  completedAt?: Date;
  resultFiles?: string[];
}