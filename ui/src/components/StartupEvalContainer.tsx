"use client";

import React, { useState, useCallback } from 'react';
import { useEffect } from 'react';
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
  const [sessionFiles, setSessionFiles] = useState<Array<{name:string, content:string}>>([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState<number | null>(null);
  const [startupName, setStartupName] = useState<string>('');
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  // startProcessingStream: starts backend processing and streams SSE events
  

  // handleFileUpload now only saves the file to pending state; actual upload happens on submit

  const handleFileUpload = useCallback(async (file: File) => {
    setPendingFile(file);
  }, []);

  const startProcessingStream = useCallback(async (fileName: string, userId: string, sessionId: string, filePath?: string | null, sessionIdForFetch?: string, userIdForFetch?: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/process-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName,
          filePath,
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

              // If this is the final result (fetch session files regardless of markdown)
              if (data.type === 'final') {
                if (data.markdown) {
                  setMarkdownContent(data.markdown);
                }
                setSession(prev => prev ? { ...prev, status: 'completed', completedAt: new Date() } : null);
                toast.success('Processing completed!');
                // Fetch session files for tabs (attempt best-effort)
                try {
                  const sid = sessionIdForFetch || sessionId
                  const uid = userIdForFetch || userId
                  const resp = await fetch('/api/sessions/files', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sessionId: sid, userId: uid }),
                  })
                  if (resp.ok) {
                    const json = await resp.json()
                    setSessionFiles(json.files || [])
                    if ((json.files || []).length > 0) setSelectedFileIndex(0)
                  }
                } catch (e) {
                  // ignore fetch errors
                }
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

  // Poll for session files while processing is active
  useEffect(() => {
    if (!session) return;
    let interval: NodeJS.Timeout | null = null;
    const fetchFiles = async (overrideDir?: string) => {
      try {
        const payload: any = { sessionId: session.id, userId: session.userId || 'user_1' }
        if (overrideDir) payload.sessionDirname = overrideDir
        const resp = await fetch('/api/sessions/files', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (resp.ok) {
          const json = await resp.json();
          const files = json.files || [];
          setSessionFiles(files);
          if (files.length > 0 && selectedFileIndex === null) {
            setSelectedFileIndex(0);
          }
          // set debug info
          setPollingDebug(`polled: sessions/${session.userId || 'user_1'}_${session.id}_startup-eval -> ${files.length} files`)
        }
      } catch (e) {
        // ignore
      }
    }

    if (isProcessing) {
      // immediate fetch then poll
      fetchFiles();
      interval = setInterval(fetchFiles, 2000);
    } else {
      // ensure one final fetch after processing finishes
      fetchFiles();
    }

    return () => {
      if (interval) clearInterval(interval);
    }
  }, [session, isProcessing, selectedFileIndex]);

  const [pollingDebug, setPollingDebug] = useState<string>('');

  const handleSubmit = useCallback(async () => {
    const normalizedUserId = (startupName || '').toString().trim() || 'user_1'
    if (!startupName || !startupName.trim()) {
      toast.error('Please enter a startup name (used as user id)')
      return
    }
    if (!pendingFile) {
      toast.error('Please select a file to upload')
      return
    }

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', pendingFile)

      const response = await fetch('/api/upload', { method: 'POST', body: formData })
      if (!response.ok) throw new Error('Upload failed')
      const result = await response.json()

      const storedFilename = result?.filename || pendingFile.name
      const storedFilePath = result?.file_path || null

      const timestampId = `session_${Date.now()}`
      const newSession: ProcessingSession = {
        id: timestampId,
        userId: normalizedUserId,
        file: {
          name: storedFilename,
          size: pendingFile.size,
          type: pendingFile.type,
          uploadedAt: new Date(),
        },
        status: 'processing',
        events: [],
        createdAt: new Date(),
      }

      setSession(newSession)
      setEvents([])
      setMarkdownContent('')
      toast.success('File uploaded — starting processing...')

  await startProcessingStream(storedFilename, newSession.userId, newSession.id, storedFilePath, newSession.id, newSession.userId)

    } catch (err) {
      console.error(err)
      toast.error('Upload or processing start failed')
    } finally {
      setIsUploading(false)
      setPendingFile(null)
    }
  }, [startupName, pendingFile, startProcessingStream])

 

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

        {/* File Upload + Startup name form */}
        {!session && (
          <div className="max-w-3xl mx-auto bg-slate-800 p-6 rounded-xl shadow-lg">
            <div className="mb-4">
              <label className="block text-sm text-slate-300 mb-2">Startup Name (used as user id)</label>
              <input
                value={startupName}
                onChange={(e) => setStartupName(e.target.value)}
                placeholder="e.g. acme-corp"
                className="w-full px-3 py-2 rounded bg-slate-700 text-white border border-slate-600"
              />
            </div>

            <FileUpload 
              onFileUpload={handleFileUpload} 
              isUploading={isUploading}
              acceptedTypes={['.pdf', '.doc', '.docx', '.txt']}
            />

            {pendingFile && (
              <div className="mt-4 bg-slate-700 p-3 rounded flex items-center justify-between text-slate-200">
                <div>
                  <div className="font-semibold">{pendingFile.name}</div>
                  <div className="text-sm text-slate-400">{Math.round(pendingFile.size/1024)} KB {pendingFile.type ? `• ${pendingFile.type}` : ''}</div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPendingFile(null)}
                    className="px-3 py-1 bg-red-600 rounded hover:opacity-90 text-white"
                  >
                    Remove
                  </button>
                </div>
              </div>
            )}

            <div className="mt-4 flex justify-end">
              <button
                onClick={handleSubmit}
                className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg shadow hover:opacity-95"
              >
                Submit & Start Processing
              </button>
            </div>
          </div>
        )}

        {/* Processing Timeline */}
        {session && (
          <div className="max-w-4xl mx-auto space-y-4">
            <div className="bg-slate-800 p-4 rounded-lg shadow-inner text-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-400">Uploaded file</div>
                  <div className="text-lg font-semibold">{session.file?.name || 'Unknown'}</div>
                  <div className="text-sm text-slate-400">{session.file?.size ? `${Math.round(session.file.size/1024)} KB` : ''} {session.file?.type ? `• ${session.file.type}` : ''}</div>
                </div>
                <div className="text-sm text-slate-400">{session.createdAt ? new Date(session.createdAt).toLocaleString() : ''}</div>
              </div>
            </div>

            <ProcessingTimeline 
              events={events}
              isLoading={isProcessing}
            />
          </div>
        )}
          {/* Results with tabs (visible as soon as session starts) */}
          {session && (
            <div>
              {/* Tabs list */}
              <div className="w-full max-w-4xl mx-auto mb-4 flex gap-2">
                {/* Default Analysis Report tab */}
                <button
                  onClick={() => setSelectedFileIndex(null)}
                  className={`px-3 py-2 rounded ${selectedFileIndex===null ? 'bg-primary text-white' : 'bg-muted text-foreground'}`}
                >
                  Analysis Report
                </button>

                {sessionFiles.length === 0 && (
                  <div className="px-4 py-2 bg-muted text-foreground rounded">No result files available yet</div>
                )}
                {sessionFiles.map((f, idx) => (
                  <button
                    key={f.name}
                    onClick={() => setSelectedFileIndex(idx)}
                    className={`px-3 py-2 rounded ${selectedFileIndex===idx ? 'bg-primary text-white' : 'bg-muted text-foreground'}`}
                  >
                    {f.name}
                  </button>
                ))}
              </div>

                {/* Debug info about polling */}
                <div className="max-w-4xl mx-auto text-sm text-slate-400 mb-4">{pollingDebug}</div>

              {/* Selected file viewer */}
              {selectedFileIndex !== null && sessionFiles[selectedFileIndex] ? (
                (() => {
                  const file = sessionFiles[selectedFileIndex]
                  if (file.name.endsWith('.md')) {
                    return (
                      <MarkdownRenderer
                        content={file.content}
                        title={file.name}
                        fileName={file.name}
                        onDownload={() => {
                          const blob = new Blob([file.content], { type: 'text/markdown' })
                          const url = URL.createObjectURL(blob)
                          const a = document.createElement('a')
                          a.href = url
                          a.download = file.name
                          document.body.appendChild(a)
                          a.click()
                          document.body.removeChild(a)
                          URL.revokeObjectURL(url)
                        }}
                      />
                    )
                  }

                  if (file.name.endsWith('.json')) {
                    return (
                      <div className="w-full max-w-4xl mx-auto bg-muted p-4 rounded">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-lg font-semibold">{file.name}</h3>
                          <button
                            onClick={() => {
                              const blob = new Blob([file.content], { type: 'application/json' })
                              const url = URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.download = file.name
                              document.body.appendChild(a)
                              a.click()
                              document.body.removeChild(a)
                              URL.revokeObjectURL(url)
                            }}
                            className="px-2 py-1 bg-slate-700 text-white rounded"
                          >
                            Download
                          </button>
                        </div>
                        <pre className="whitespace-pre-wrap text-sm">{file.content}</pre>
                      </div>
                    )
                  }

                  return <div className="w-full max-w-4xl mx-auto p-4">Unsupported file type</div>
                })()
              ) : (
                <MarkdownRenderer
                  content={markdownContent || 'No report content was produced by the processing pipeline.'}
                  title="Analysis Report"
                  fileName={`${session?.file.name}_analysis.md`}
                  onDownload={handleDownloadReport}
                />
              )}
            </div>
          )}

        {/* Reset Button */}
        {session && !isProcessing && !isUploading && (
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