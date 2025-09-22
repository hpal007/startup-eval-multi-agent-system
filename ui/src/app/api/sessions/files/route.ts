import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
  const body = await request.json()
  const sessionId = body.sessionId
  let userId = (body.userId || 'user_1')
  userId = String(userId).trim() || 'user_1'
  // Optional: accept a precomputed sessionDirname (from backend SSE)
  const sessionDirname = body.sessionDirname

    if (!sessionId) {
      return NextResponse.json({ error: 'sessionId required' }, { status: 400 })
    }

    // Sessions are stored in repo relative `sessions` dir
    const repoRoot = process.cwd()
    const sessionsDir = path.join(repoRoot, 'sessions')

  // Directory naming appears to be `${userId}_${sessionId}_startup-eval` or `${userId}_session_${sessionId}_startup-eval`
  const dirName = sessionDirname || `${userId}_${sessionId}_startup-eval`
    const sessionPath = path.join(sessionsDir, dirName)

    console.log('[sessions/files] checking path:', sessionPath)
    if (!fs.existsSync(sessionPath)) {
      console.log('[sessions/files] path does not exist')
      return NextResponse.json({ files: [] })
    }

    const entries = fs.readdirSync(sessionPath)
      .filter(f => f.endsWith('.md') || f.endsWith('.json'))
      .sort()

    const files = entries.map((fname) => {
      const full = path.join(sessionPath, fname)
      const content = fs.readFileSync(full, { encoding: 'utf-8' })
      return { name: fname, content }
    })

    return NextResponse.json({ files })
  } catch (error) {
    console.error('sessions/files error', error)
    return NextResponse.json({ error: 'failed' }, { status: 500 })
  }
}
