# Startup Evaluation UI

This is a Next.js web interface for the startup evaluation multi-agent system.

## Features

- **File Upload**: Simple drag-and-drop interface for PDF and document files
- **Real-time Processing**: Live streaming of multi-agent processing logs
- **Markdown Rendering**: Dynamic rendering of generated analysis reports
- **Minimalist Design**: Clean, responsive interface with dark theme

## Getting Started

### Prerequisites

- Node.js 18+ (LTS recommended)
- Backend system running on `http://127.0.0.1:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Build

```bash
npm run build
npm start
```

## Environment Configuration

Create a `.env.local` file:

```env
BACKEND_URL=http://127.0.0.1:8000
NODE_ENV=development
```

## API Endpoints

- `/api/upload` - File upload endpoint
- `/api/process-stream` - SSE streaming for processing logs

## Architecture

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React hooks
- **Streaming**: Server-Sent Events (SSE)
- **File Handling**: Native File API

## Components

- `FileUpload` - Drag-and-drop file upload interface
- `ProcessingTimeline` - Real-time processing event timeline
- `MarkdownRenderer` - Formatted markdown display
- `StartupEvalContainer` - Main application container

## Testing

```bash
npm test
npm run lint
npm run type-check
```