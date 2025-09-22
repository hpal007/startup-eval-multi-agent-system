import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Get backend URL from environment
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    
    // Create FormData for backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    // Forward to backend
    console.log('[api/upload] forwarding to backend:', backendUrl);
    const response = await fetch(`${backendUrl}/upload`, {
      method: 'POST',
      body: backendFormData,
    });

    console.log('[api/upload] backend response status:', response.status);

    if (!response.ok) {
      const text = await response.text().catch(() => '<no body>');
      console.error('[api/upload] backend error body:', text);
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const result = await response.json();
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    );
  }
}