import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { fileName, filePath, userId = "user_1", sessionId = "session_001" } = await request.json();
    
    if (!fileName && !filePath) {
      return NextResponse.json({ error: 'No file name or path provided' }, { status: 400 });
    }

    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    
    // Create SSE stream
    const encoder = new TextEncoder();
    
    const stream = new ReadableStream({
      async start(controller) {
        try {
          // Start processing request to backend
          console.log('[api/process-stream] calling backend process endpoint:', backendUrl + '/process');
          const response = await fetch(`${backendUrl}/process`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              query: `Process the uploaded file: ${fileName || filePath}`,
              filePath: filePath,
              filename: fileName,
              user_id: userId,
              session_id: sessionId,
              streaming: true
            }),
          });

          if (!response.ok) {
            const body = await response.text().catch(() => '<no body>');
            console.error('[api/process-stream] backend returned error body:', body);
            throw new Error(`Backend responded with status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('No readable stream from backend');
          }

          // Stream the response
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            // Forward the chunk to the client
            controller.enqueue(value);
          }
          
          controller.close();
        } catch (error) {
          console.error('Stream error:', error);
          const errorMessage = `data: ${JSON.stringify({ 
            type: 'error', 
            content: 'Processing failed' 
          })}\n\n`;
          controller.enqueue(encoder.encode(errorMessage));
          controller.close();
        }
      },
    });

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Process stream error:', error);
    return NextResponse.json(
      { error: 'Failed to start processing stream' },
      { status: 500 }
    );
  }
}