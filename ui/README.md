# Startup Evaluation System - Web UI

A minimalist web interface for the multi-agent startup evaluation system. This UI allows users to upload PDF documents and view real-time processing logs and analysis results.

## Features

- 📁 **File Upload**: Simple drag-and-drop PDF upload interface
- ⚡ **Real-time Processing**: Live progress tracking and log streaming
- 📊 **Interactive Reports**: Tabbed interface for different analysis sections
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🎨 **Minimalist UI**: Clean, modern design with smooth animations
- 📄 **Markdown Rendering**: Dynamic conversion of .md reports to formatted HTML

## Project Structure

```
ui/
├── index.html          # Main application interface
├── css/
│   └── styles.css      # Minimalist styling and animations
├── js/
│   └── app.js          # Core application logic
├── assets/             # Static assets (images, icons, etc.)
├── server.py           # Demo Flask backend server
├── requirements.txt    # Python dependencies for demo server
└── README.md          # This file
```

## Quick Start

### Option 1: Demo Mode (Standalone)

1. **Install demo server dependencies:**
   ```bash
   cd ui
   pip install -r requirements.txt
   ```

2. **Start the demo server:**
   ```bash
   python server.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

4. **Test the interface:**
   - Upload a PDF file
   - Watch the real-time processing simulation
   - View the generated analysis reports

### Option 2: Integration with Backend

To integrate with your actual multi-agent backend system:

1. **Serve the static files** from your web server
2. **Implement the API endpoints** (see API section below)
3. **Set up WebSocket support** for real-time updates (optional)
4. **Customize the UI** as needed for your specific use case

## API Endpoints

The UI expects the following backend endpoints:

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

Response:
{
  "processId": "uuid-string",
  "status": "started",
  "message": "Processing started"
}
```

### Status Check
```http
GET /api/status/{processId}

Response:
{
  "processId": "uuid-string",
  "status": "processing|completed|error",
  "stage": 0-3,
  "progress": 0-100,
  "logs": [
    {
      "message": "Log message",
      "type": "system|success|warning|error",
      "timestamp": "HH:MM:SS"
    }
  ]
}
```

### Results Retrieval
```http
GET /api/results/{processId}

Response:
{
  "executive": "# Executive Summary markdown...",
  "founders": "# Founder Analysis markdown...",
  "competitors": "# Competitive Analysis markdown...",
  "kpis": "# KPI Analysis markdown...",
  "full": "# Complete Report markdown..."
}
```

### WebSocket Events (Optional)

For real-time updates, implement WebSocket support:

```javascript
// Connect to process room
socket.emit('join_process', { processId: 'uuid' });

// Listen for progress updates
socket.on('progress_update', (data) => {
  // Handle real-time progress updates
});
```

## Integration with Multi-Agent Backend

To connect this UI with your existing multi-agent system:

### 1. File Upload Integration

```python
# In your main.py or web server
from tools.file_tool import upload_tool
from workflow.master.agent import root_agent

@app.route('/api/upload', methods=['POST'])
async def upload_document():
    file = request.files['file']
    
    # Use your existing upload tool
    process_id = str(uuid.uuid4())
    
    # Start processing with your master agent
    result = await root_agent.process(
        file_content=file.read(),
        session_id=process_id
    )
    
    return jsonify({
        'processId': process_id,
        'status': 'started'
    })
```

### 2. Progress Monitoring

```python
# Add progress callbacks to your agents
def progress_callback(stage, message, progress):
    socketio.emit('progress_update', {
        'stage': stage,
        'message': message,
        'progress': progress,
        'logs': [{'message': message, 'type': 'system'}]
    }, room=process_id)

# Update your agent callbacks
async def before_agent_callback(callback_context):
    progress_callback(0, "Starting PDF processing...", 10)
```

### 3. Results Integration

```python
# Serve your generated markdown files
@app.route('/api/results/<process_id>')
def get_results(process_id):
    session_dir = get_session_dir(process_id)
    
    results = {}
    for report_type in ['executive', 'founders', 'competitors', 'kpis']:
        file_path = os.path.join(session_dir, f"{report_type}_report.md")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                results[report_type] = f.read()
    
    return jsonify(results)
```

## Customization

### Styling

The UI uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --error-color: #ef4444;
    /* Customize other colors */
}
```

### Processing Stages

Update the processing stages in `app.js`:

```javascript
this.stages = [
    { id: 'stage1', name: 'Your Stage 1', description: 'Custom description' },
    { id: 'stage2', name: 'Your Stage 2', description: 'Custom description' },
    // Add more stages as needed
];
```

### Report Tabs

Modify the report tabs by updating the HTML and JavaScript:

```html
<!-- Add new tab button -->
<button class="tab-button" data-tab="newtab">New Analysis</button>

<!-- Add corresponding content -->
<div class="tab-content" id="tab-newtab">
    <div class="markdown-content" id="newtabContent"></div>
</div>
```

## Browser Support

- ✅ Chrome 70+
- ✅ Firefox 65+
- ✅ Safari 12+
- ✅ Edge 79+
- ⚠️ IE 11 (limited support)

## Features in Detail

### File Upload
- Drag-and-drop support
- File type validation (PDF only)
- File size limits (configurable)
- Progress indication
- Error handling

### Real-time Processing
- WebSocket connections for live updates
- Fallback to HTTP polling
- Stage-based progress tracking
- Colored log entries by type
- Auto-scrolling log display

### Report Display
- Markdown-to-HTML conversion
- Syntax highlighting for code blocks
- Responsive table formatting
- Tabbed navigation
- Print-friendly styling

### Responsive Design
- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interfaces
- Adaptive typography
- Dark mode support (system preference)

## Performance Considerations

- **Lazy Loading**: Large reports are loaded on-demand
- **Memory Management**: Log entries are limited to prevent memory leaks
- **Connection Handling**: Automatic WebSocket reconnection
- **Caching**: Static assets are cached for performance
- **Compression**: Enable gzip compression on your web server

## Security Notes

- **File Validation**: Only PDF files are accepted
- **Size Limits**: Configurable file size limits
- **CSRF Protection**: Implement CSRF tokens in production
- **Rate Limiting**: Add rate limiting to prevent abuse
- **Authentication**: Add user authentication as needed

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file type (must be PDF)
   - Verify file size limit
   - Ensure backend is running

2. **Real-time Updates Not Working**
   - Check WebSocket connection
   - Verify CORS settings
   - Check browser console for errors

3. **Reports Not Displaying**
   - Verify markdown content format
   - Check API response structure
   - Look for JavaScript console errors

### Debug Mode

Enable debug logging in the browser console:

```javascript
localStorage.setItem('debug', 'true');
// Reload the page to see debug logs
```

## Contributing

To contribute to the UI:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Startup Evaluation Multi-Agent System. See the main project license for details.

---

**Note**: This UI is designed to work with the existing multi-agent backend system. The demo server is for testing purposes only and should not be used in production.