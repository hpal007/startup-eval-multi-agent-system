import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    
    // Try to connect to the backend health endpoint
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({
        status: 'healthy',
        backend: 'connected',
        backendUrl,
        backendData: data,
      });
    } else {
      return NextResponse.json({
        status: 'degraded',
        backend: 'error',
        backendUrl,
        error: `Backend responded with status: ${response.status}`,
      }, { status: 503 });
    }
  } catch (error) {
    return NextResponse.json({
      status: 'unhealthy',
      backend: 'disconnected',
      backendUrl: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
      error: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 503 });
  }

}