"use client";

import React, { useState, useCallback } from 'react';
import { FileUpload } from './FileUpload';
import { ProcessingTimeline } from './ProcessingTimeline';
import { MarkdownRenderer } from './MarkdownRenderer';
import { ProcessingEvent, ProcessingSession } from '@/lib/types';
import { toast } from 'sonner';

export function StartupEvalContainer() {
  const [session, setSession] = useState<ProcessingSession | null>(null);
  const [events, setEvents] = useState<ProcessingEvent[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [markdownContent, setMarkdownContent] = useState<string>('');

  const handleFileUpload = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      
      // Create session
      const newSession: ProcessingSession = {
        id: `session_${Date.now()}`,
        userId: 'user_1',
        file: {
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date(),
        },
        status: 'processing',
        events: [],
        createdAt: new Date(),
      };

      setSession(newSession);
      setEvents([]);
      setMarkdownContent('');
      
      toast.success('File uploaded successfully! Starting processing...');
      
      // Start processing stream
      await startProcessingStream(file.name, newSession.userId, newSession.id);
      
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload file');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const startProcessingStream = useCallback(async (fileName: string, userId: string, sessionId: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/process-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName,
          userId,
          sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start processing');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No stream reader available');
      }

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              const event: ProcessingEvent = {
                type: data.type || 'progress',
                content: data.content || data.message || 'Processing...',
                timestamp: new Date(),
                agentName: data.agent || data.agentName,
                metadata: data.metadata,
              };

              setEvents(prev => [...prev, event]);

              // If this is the final result with markdown content
              if (data.type === 'final' && data.markdown) {
                setMarkdownContent(data.markdown);
                setSession(prev => prev ? { ...prev, status: 'completed', completedAt: new Date() } : null);
                toast.success('Processing completed!');
              }
            } catch (parseError) {
              console.error('Failed to parse SSE data:', parseError);
            }
          }
        }
      }
    } catch (error) {
      console.error('Processing stream error:', error);
      const errorEvent: ProcessingEvent = {
        type: 'error',
        content: 'Processing failed. Please try again.',
        timestamp: new Date(),
      };
      setEvents(prev => [...prev, errorEvent]);
      setSession(prev => prev ? { ...prev, status: 'error' } : null);
      toast.error('Processing failed');
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const handleDownloadReport = useCallback(() => {
    if (!markdownContent) return;
    
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${session?.file.name || 'report'}_analysis.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [markdownContent, session]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-white">
            Startup Evaluation System
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Upload your startup pitch deck and let our multi-agent system analyze and provide comprehensive insights
          </p>
        </div>

        {/* File Upload */}
        {!session && (
          <FileUpload 
            onFileUpload={handleFileUpload} 
            isUploading={isUploading}
            acceptedTypes={['.pdf', '.doc', '.docx', '.txt']}
          />
        )}

        {/* Processing Timeline */}
        {session && (
          <ProcessingTimeline 
            events={events}
            isLoading={isProcessing}
          />
        )}

        {/* Results */}
        {markdownContent && (
          <MarkdownRenderer
            content={markdownContent}
            title="Analysis Report"
            fileName={`${session?.file.name}_analysis.md`}
            onDownload={handleDownloadReport}
          />
        )}

        {/* Reset Button */}
        {session && !isProcessing && (
          <div className="text-center">
            <button
              onClick={() => {
                setSession(null);
                setEvents([]);
                setMarkdownContent('');
              }}
              className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Upload Another File
            </button>
          </div>
        )}
      </div>
    </div>
  );
}