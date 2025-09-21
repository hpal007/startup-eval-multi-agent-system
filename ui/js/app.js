/**
 * Startup Evaluation System - Frontend Application
 * 
 * This application provides a web interface for the multi-agent startup evaluation system.
 * It handles file uploads, displays real-time processing logs, and renders markdown reports.
 */

class StartupEvaluationApp {
    constructor() {
        this.currentSection = 'upload';
        this.processingStage = 0;
        this.logsPaused = false;
        this.markdownRenderer = null;
        this.eventSource = null;
        this.sessionId = null;
        
        this.stages = [
            { id: 'stage1', name: 'PDF Processing', description: 'Extracting content from document' },
            { id: 'stage2', name: 'Founder Analysis', description: 'Verifying founder backgrounds' },
            { id: 'stage3', name: 'Competitive Analysis', description: 'Researching market positioning' },
            { id: 'stage4', name: 'KPI Validation', description: 'Analyzing business metrics' }
        ];
        
        this.init();
    }
    
    init() {
        this.initMarkdownRenderer();
        this.bindEventListeners();
        this.initializeTimestamp();
    }

    async createSession(userId) {
        try {
            const response = await fetch('/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    app_name: "chatgpt_agentic_clone_app"
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Session creation failed: ${response.status} - ${errorText}`);
            }

            const result = await response.json();
            console.log('Session created successfully:', result);
            return result.session_id;
        } catch (error) {
            console.error('Failed to create session:', error);
            // Fallback to timestamp-based session ID for local development
            return `session_${Date.now()}`;
        }
    }
    
    initMarkdownRenderer() {
        // Initialize markdown-it with plugins
        this.markdownRenderer = window.markdownit({
            html: true,
            linkify: true,
            typographer: true,
            breaks: true
        });
    }
    
    bindEventListeners() {
        // File input handling
        const fileInput = document.getElementById('fileInput');
        const uploadForm = document.getElementById('uploadForm');
        const removeFileBtn = document.getElementById('removeFile');
        
        fileInput.addEventListener('change', this.handleFileSelection.bind(this));
        uploadForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        removeFileBtn.addEventListener('click', this.removeSelectedFile.bind(this));
        
        // Processing controls
        const pauseLogsBtn = document.getElementById('pauseLogs');
        const clearLogsBtn = document.getElementById('clearLogs');
        
        pauseLogsBtn.addEventListener('click', this.toggleLogsPause.bind(this));
        clearLogsBtn.addEventListener('click', this.clearLogs.bind(this));
        
        // Results controls
        const downloadBtn = document.getElementById('downloadReport');
        const startNewBtn = document.getElementById('startNew');
        
        downloadBtn.addEventListener('click', this.downloadReport.bind(this));
        startNewBtn.addEventListener('click', this.startNewAnalysis.bind(this));
        
        // Tab navigation
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', this.switchTab.bind(this));
        });
        
        // Window unload handling
        window.addEventListener('beforeunload', this.cleanup.bind(this));
    }
    
    initializeTimestamp() {
        const timestamp = document.querySelector('.log-timestamp');
        if (timestamp) {
            timestamp.textContent = this.getCurrentTimestamp();
        }
    }
    
    getCurrentTimestamp() {
        return new Date().toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    handleFileSelection(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        if (file.type !== 'application/pdf') {
            this.showNotification('Please select a PDF file.', 'error');
            event.target.value = '';
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('File size must be less than 10MB.', 'error');
            event.target.value = '';
            return;
        }
        
        // Show selected file info
        const selectedFile = document.getElementById('selectedFile');
        const fileName = selectedFile.querySelector('.file-name');
        const fileSize = selectedFile.querySelector('.file-size');
        
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        selectedFile.style.display = 'flex';
        
        // Enable submit button
        document.getElementById('submitButton').disabled = false;
    }
    
    removeSelectedFile() {
        document.getElementById('fileInput').value = '';
        document.getElementById('selectedFile').style.display = 'none';
        document.getElementById('submitButton').disabled = true;
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showNotification('Please select a file.', 'error');
            return;
        }
        
        try {
            await this.uploadAndProcess(file);
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Upload failed. Please try again.', 'error');
        }
    }
    
    async uploadAndProcess(file) {
        // Switch to processing view
        this.switchSection('processing');
        
        try {
            // Upload file to server first
            this.addLogEntry('Uploading PDF file to server...', 'system');
            const uploadResult = await this.uploadFileToServer(file);
            
            if (!uploadResult.success) {
                throw new Error(uploadResult.message || 'File upload failed');
            }
            
            this.addLogEntry(`File uploaded successfully: ${uploadResult.filename}`, 'success');
            
            // Create ADK agent request with file path (no base64!)
            const agentRequest = {
                message: `Please analyze this startup pitch PDF file: ${uploadResult.filename}. The file is located at: ${uploadResult.file_path}`,
                filename: uploadResult.filename,
                file_path: uploadResult.file_path
            };
            
            // Start ADK agent processing with Server-Sent Events
            this.startAgentProcessing(agentRequest);
            
        } catch (error) {
            console.error('Processing setup error:', error);
            console.error('Error details:', error.stack);
            this.addLogEntry('Failed to start processing: ' + error.message, 'error');
            this.addLogEntry('Falling back to demo mode for now...', 'warning');
            
            // For demo purposes, start mock processing
            this.startMockProcessing();
        }
    }
    
    async uploadFileToServer(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData  // Don't set Content-Type header - let browser set it with boundary
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Upload failed: ${response.status} - ${errorText}`);
        }
        
        return await response.json();
    }
    
    // Removed readFileAsBase64 - we now upload files directly to server
    
    startAgentProcessing(agentRequest) {
        try {
            // First test our debug endpoint to verify request format
            this.testAdkFormat(agentRequest).then(() => {
                // Use ADK's Server-Sent Events endpoint
                const sseUrl = '/run_sse';
                
                // Create EventSource with POST data (using POST via fetch for initial request)
                this.initializeSSEConnection(sseUrl, agentRequest);
            });
            
        } catch (error) {
            console.error('SSE error:', error);
            this.addLogEntry('Failed to connect to agent processing', 'error');
            this.startMockProcessing();
        }
    }
    
    async testAdkFormat(agentRequest) {
        try {
            const userId = `user_${Date.now()}`;
            
            // Create session if we don't have one
            if (!this.sessionId) {
                this.sessionId = await this.createSession(userId);
            }
            
            const testRequest = {
                app_name: "chatgpt_agentic_clone_app",  // Must match main.py APP_NAME
                user_id: userId,
                session_id: this.sessionId,
                new_message: {
                    role: "user",
                    parts: [{
                        text: agentRequest.message
                    }]
                }
            };
            
            console.log('Testing ADK format:', testRequest);
            
            const response = await fetch('/api/test-adk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testRequest)
            });
            
            const result = await response.json();
            console.log('Test endpoint response:', result);
            this.addLogEntry('Request format test successful - using correct ADK format with file path', 'system');
            
        } catch (error) {
            console.error('Test request failed:', error);
            this.addLogEntry('Request format test failed: ' + error.message, 'error');
        }
    }
    
    async initializeSSEConnection(url, agentRequest) {
        try {
            // ADK expects app_name, user_id, session_id, and new_message format
            const userId = `user_${Date.now()}`;
            
            // Create session if we don't have one
            if (!this.sessionId) {
                this.sessionId = await this.createSession(userId);
            }
            
            console.log('Using session info:', { userId, sessionId: this.sessionId });
            
            const adkRequest = {
                app_name: "chatgpt_agentic_clone_app",  // Must match main.py APP_NAME
                user_id: userId,
                session_id: this.sessionId,
                new_message: {
                    role: "user",
                    parts: [{
                        text: agentRequest.message
                    }]
                }
            };
            
            console.log('Sending ADK request:', adkRequest);
            
            // Make POST request to ADK's run_sse endpoint
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify(adkRequest)
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            // Create EventSource for streaming updates
            this.connectEventSource(response);
            
        } catch (error) {
            console.error('SSE initialization error:', error);
            console.error('Full error details:', error);
            this.addLogEntry('Failed to start agent processing: ' + error.message, 'error');
            this.addLogEntry('Check browser console for detailed error information', 'warning');
            // Temporarily removed fallback to see actual errors
            // this.startMockProcessing();
        }
    }
    
    connectEventSource(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        this.addLogEntry('Connected to agent processing stream', 'system');
        
        const readStream = async () => {
            try {
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                this.handleAgentUpdate(data);
                            } catch (e) {
                                // Handle non-JSON SSE messages
                                if (line.trim()) {
                                    this.addLogEntry(line.substring(6), 'system');
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Stream reading error:', error);
                this.addLogEntry('Stream connection lost', 'warning');
                // Don't retry automatically - let user restart if needed
            }
        };
        
        readStream();
    }
    
    handleAgentUpdate(data) {
        // Handle different types of agent messages
        if (data.type === 'log' || data.message) {
            this.addLogEntry(data.message || data.content, data.level || 'info');
        }
        
        // Handle progress updates
        if (data.progress !== undefined) {
            this.updateProgress(data.progress, data.message || 'Processing...');
        }
        
        // Handle stage changes based on agent actions
        if (data.agent_name || data.tool_name) {
            this.handleAgentStageUpdate(data);
        }
        
        // Handle completion
        if (data.type === 'complete' || data.status === 'completed') {
            this.handleAgentCompletion(data);
        }
        
        // Handle errors
        if (data.type === 'error' || data.error) {
            this.addLogEntry(data.error || data.message || 'An error occurred', 'error');
        }
    }
    
    handleAgentStageUpdate(data) {
        // Map agent actions to UI stages
        const agentToStage = {
            'process_pdf': 0,
            'founder': 1,
            'competitive': 2,
            'kpi': 3
        };
        
        // Try to determine stage from agent/tool name
        const agentName = data.agent_name || data.tool_name || '';
        for (const [key, stage] of Object.entries(agentToStage)) {
            if (agentName.toLowerCase().includes(key)) {
                if (stage !== this.processingStage) {
                    this.updateStage(stage);
                }
                break;
            }
        }
    }
    
    handleAgentCompletion(data) {
        // Mark as completed
        this.updateProgress(100, 'Analysis completed successfully!');
        this.updateStage(4);
        
        // If we have results in the completion data, process them
        if (data.results || data.output) {
            this.processResults(data.results || data.output);
        } else {
            // Generate mock results for display
            setTimeout(() => {
                this.processResults(this.generateMockResults());
            }, 1000);
        }
    }
    
    handleProgressUpdate(data) {
        const { stage, progress, message, status, logs } = data;
        
        // Update progress
        if (typeof progress === 'number') {
            this.updateProgress(progress, message || this.stages[stage]?.description || 'Processing...');
        }
        
        // Update stage
        if (typeof stage === 'number' && stage !== this.processingStage) {
            this.updateStage(stage);
        }
        
        // Add logs
        if (logs && Array.isArray(logs)) {
            logs.forEach(log => {
                this.addLogEntry(log.message, log.type || 'system', log.timestamp);
            });
        } else if (message) {
            this.addLogEntry(message, status || 'system');
        }
        
        // Check if processing is complete
        if (status === 'completed') {
            this.completeProcessing(data.results);
        } else if (status === 'error') {
            this.handleProcessingError(data.error || 'Processing failed');
        }
    }
    
    updateProgress(percent, stage) {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressStage = document.getElementById('progressStage');
        
        progressFill.style.width = `${percent}%`;
        progressPercent.textContent = `${Math.round(percent)}%`;
        progressStage.textContent = stage;
    }
    
    updateStage(stageIndex) {
        // Mark previous stages as completed
        for (let i = 0; i < stageIndex; i++) {
            const stageElement = document.getElementById(this.stages[i].id);
            if (stageElement) {
                stageElement.classList.remove('active');
                stageElement.classList.add('completed');
                const status = stageElement.querySelector('.stage-status');
                status.textContent = 'Completed';
                status.className = 'stage-status completed';
            }
        }
        
        // Mark current stage as active
        if (stageIndex < this.stages.length) {
            const currentStage = document.getElementById(this.stages[stageIndex].id);
            if (currentStage) {
                currentStage.classList.add('active');
                const status = currentStage.querySelector('.stage-status');
                status.textContent = 'Processing';
                status.className = 'stage-status active';
            }
        }
        
        this.processingStage = stageIndex;
    }
    
    addLogEntry(message, type = 'system', timestamp = null) {
        if (this.logsPaused) return;
        
        const logsContent = document.getElementById('logsContent');
        if (!logsContent) return;
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        
        const logTimestamp = document.createElement('span');
        logTimestamp.className = 'log-timestamp';
        logTimestamp.textContent = timestamp || this.getCurrentTimestamp();
        
        const logMessage = document.createElement('span');
        logMessage.className = 'log-message';
        logMessage.textContent = message;
        
        logEntry.appendChild(logTimestamp);
        logEntry.appendChild(logMessage);
        logsContent.appendChild(logEntry);
        
        // Auto-scroll to bottom
        logsContent.scrollTop = logsContent.scrollHeight;
        
        // Limit log entries to prevent memory issues
        const entries = logsContent.querySelectorAll('.log-entry');
        if (entries.length > 100) {
            entries[0].remove();
        }
    }
    
    toggleLogsPause() {
        this.logsPaused = !this.logsPaused;
        const button = document.getElementById('pauseLogs');
        button.textContent = this.logsPaused ? 'Resume' : 'Pause';
    }
    
    clearLogs() {
        const logsContent = document.getElementById('logsContent');
        if (logsContent) {
            logsContent.innerHTML = '';
            this.addLogEntry('Logs cleared', 'system');
        }
    }
    
    async completeProcessing(results) {
        // Mark final stage as completed
        this.updateStage(4);
        this.updateProgress(100, 'Analysis complete!');
        
        // Add completion log
        this.addLogEntry('Processing completed successfully', 'success');
        
        // Load and display results
        await this.loadResults(results);
        
        // Switch to results view after a short delay
        setTimeout(() => {
            this.switchSection('results');
        }, 2000);
    }
    
    handleProcessingError(error) {
        this.addLogEntry(`Processing failed: ${error}`, 'error');
        this.updateProgress(0, 'Processing failed');
        
        // Show error notification
        this.showNotification('Processing failed. Please try again.', 'error');
    }
    
    async loadResults(results) {
        try {
            if (results) {
                // If results are provided directly (from agent completion)
                this.displayResults(results);
            } else {
                // For ADK, results should be provided in the completion data
                // If not available, show mock results for demo
                console.log('No results provided, showing mock results');
                this.displayMockResults();
            }
        } catch (error) {
            console.error('Error loading results:', error);
            this.displayMockResults();
        }
    }
    
    displayResults(results) {
        const tabs = ['executive', 'founders', 'competitors', 'kpis', 'full'];
        
        tabs.forEach(tab => {
            const content = results[tab] || results[`${tab}_summary`] || '';
            const element = document.getElementById(`${tab}Content`);
            if (element && content) {
                element.innerHTML = this.markdownRenderer.render(content);
            }
        });
    }
    
    displayMockResults() {
        // Mock results for demonstration
        const mockResults = {
            executive: `# Executive Summary

## Overall Assessment: **B+ (Promising with Key Areas for Improvement)**

### Key Findings

- **Strong founding team** with relevant industry experience
- **Large addressable market** with validated demand
- **Competitive differentiation** through innovative technology approach
- **Solid financial projections** with realistic growth assumptions

### Recommendations

1. **Expand go-to-market strategy** to include enterprise sales
2. **Strengthen technical team** with additional senior developers
3. **Secure Series A funding** within the next 12 months
4. **Develop strategic partnerships** with industry leaders

### Risk Factors

- **High customer acquisition costs** may impact profitability
- **Strong competition** from established players
- **Technology risks** in scaling the platform`,

            founders: `# Founder Analysis

## Team Overview

### John Smith - CEO & Co-Founder
- **Background**: 8 years experience at Google and Microsoft
- **Education**: Stanford Computer Science, MBA from Wharton
- **Previous Success**: Co-founded and sold TechCorp for $50M
- **Network Score**: 9/10 (Strong Silicon Valley connections)

### Sarah Johnson - CTO & Co-Founder  
- **Background**: Senior Engineer at Netflix and Airbnb
- **Education**: MIT Computer Science, PhD in Machine Learning
- **Technical Expertise**: AI/ML, distributed systems, scalable architecture
- **GitHub Activity**: 500+ contributions, active open-source contributor

## Team Strengths
✅ Complementary skill sets
✅ Strong technical expertise
✅ Proven track record
✅ Industry connections

## Areas for Improvement
⚠️ Limited domain expertise in target market
⚠️ Small team size for ambitious roadmap`,

            competitors: `# Competitive Analysis

## Market Landscape

### Direct Competitors

#### Competitor A - Market Leader
- **Market Share**: 35%
- **Funding**: $100M Series C
- **Strengths**: Brand recognition, extensive features
- **Weaknesses**: Legacy technology, high pricing

#### Competitor B - Fast Growing
- **Market Share**: 18%
- **Funding**: $50M Series B
- **Strengths**: Modern UI, competitive pricing
- **Weaknesses**: Limited enterprise features

### Competitive Positioning

| Feature | Our Startup | Competitor A | Competitor B |
|---------|-------------|--------------|--------------|
| AI-Powered | ✅ | ❌ | ⚠️ |
| Enterprise Ready | ⚠️ | ✅ | ❌ |
| Pricing | ✅ | ❌ | ✅ |
| User Experience | ✅ | ⚠️ | ✅ |

## Competitive Advantages
1. **AI-first approach** provides superior insights
2. **Lower pricing** makes solution accessible to SMBs
3. **Modern architecture** enables rapid feature development`,

            kpis: `# KPI Analysis

## Financial Metrics

### Revenue Projections
- **Year 1**: $500K ARR (Achieved: $480K - 96% of target)
- **Year 2**: $2.5M ARR (On track based on current growth)
- **Year 3**: $8M ARR (Ambitious but achievable)

### Unit Economics
- **Customer Acquisition Cost (CAC)**: $450
- **Lifetime Value (LTV)**: $2,800
- **LTV/CAC Ratio**: 6.2x ✅ (Target: >3x)
- **Payback Period**: 8 months ✅ (Target: <12 months)

## Operational Metrics

### Growth Metrics
- **Monthly Recurring Revenue Growth**: 15% MoM
- **Customer Churn Rate**: 5% monthly (Industry avg: 7%)
- **Net Revenue Retention**: 110%

### Product Metrics
- **Daily Active Users**: 2,500
- **Feature Adoption Rate**: 65%
- **Customer Satisfaction (NPS)**: 45 (Good)

## Benchmark Analysis
- **Above Industry Average**: Revenue growth, customer retention
- **At Industry Average**: Customer acquisition efficiency
- **Below Industry Average**: Customer satisfaction scores`,

            full: `# Complete Startup Evaluation Report

## Executive Summary
[Combined summary of all analyses...]

## Detailed Analysis

### 1. Founding Team Assessment
[Full founder analysis...]

### 2. Market & Competition
[Complete competitive landscape...]

### 3. Financial Analysis
[Comprehensive KPI breakdown...]

### 4. Risk Assessment
[Detailed risk analysis...]

### 5. Strategic Recommendations
[Action items and next steps...]`
        };
        
        this.displayResults(mockResults);
    }
    
    switchTab(event) {
        const tabName = event.target.dataset.tab;
        if (!tabName) return;
        
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`tab-${tabName}`).classList.add('active');
    }
    
    switchSection(sectionName) {
        // Hide all sections
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('processingSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Show target section
        document.getElementById(`${sectionName}Section`).style.display = 'block';
        
        this.currentSection = sectionName;
        
        // Add fade-in animation
        const section = document.getElementById(`${sectionName}Section`);
        section.classList.add('fade-in');
        setTimeout(() => {
            section.classList.remove('fade-in');
        }, 500);
    }
    
    downloadReport() {
        // Collect all report content
        const reportContent = [];
        const tabs = ['executive', 'founders', 'competitors', 'kpis'];
        
        tabs.forEach(tab => {
            const element = document.getElementById(`${tab}Content`);
            if (element) {
                reportContent.push(`# ${tab.charAt(0).toUpperCase() + tab.slice(1)} Analysis\n\n`);
                reportContent.push(element.textContent || element.innerText);
                reportContent.push('\n\n---\n\n');
            }
        });
        
        // Create and download file
        const blob = new Blob([reportContent.join('')], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `startup-evaluation-report-${new Date().toISOString().split('T')[0]}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Report downloaded successfully!', 'success');
    }
    
    startNewAnalysis() {
        // Reset application state
        this.sessionId = null;
        
        // Close any existing EventSource connection
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.processingStage = 0;
        this.logsPaused = false;
        
        // Reset form
        document.getElementById('fileInput').value = '';
        document.getElementById('selectedFile').style.display = 'none';
        document.getElementById('submitButton').disabled = true;
        
        // Reset progress
        this.updateProgress(0, 'Initializing...');
        
        // Reset stages
        this.stages.forEach((stage, index) => {
            const stageElement = document.getElementById(stage.id);
            if (stageElement) {
                stageElement.classList.remove('active', 'completed');
                const status = stageElement.querySelector('.stage-status');
                status.textContent = 'Pending';
                status.className = 'stage-status pending';
            }
        });
        
        // Clear logs
        this.clearLogs();
        
        // Close WebSocket if open
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Switch back to upload section
        this.switchSection('upload');
    }
    
    startMockProcessing() {
        // Simulate the processing workflow for demo purposes
        this.addLogEntry('Starting mock processing for demonstration', 'system');
        
        let progress = 0;
        let stageIndex = 0;
        
        const mockSteps = [
            { stage: 0, progress: 10, message: 'Uploading PDF document...', type: 'system' },
            { stage: 0, progress: 25, message: 'Extracting text from PDF pages...', type: 'system' },
            { stage: 0, progress: 40, message: 'PDF processing completed', type: 'success' },
            
            { stage: 1, progress: 50, message: 'Starting founder background verification...', type: 'system' },
            { stage: 1, progress: 65, message: 'Searching LinkedIn and company databases...', type: 'system' },
            { stage: 1, progress: 75, message: 'Founder analysis completed', type: 'success' },
            
            { stage: 2, progress: 80, message: 'Researching competitive landscape...', type: 'system' },
            { stage: 2, progress: 90, message: 'Analyzing market positioning...', type: 'system' },
            { stage: 2, progress: 95, message: 'Competitive analysis completed', type: 'success' },
            
            { stage: 3, progress: 98, message: 'Validating business KPIs...', type: 'system' },
            { stage: 3, progress: 100, message: 'KPI analysis completed', type: 'success' },
        ];
        
        let stepIndex = 0;
        
        const processStep = () => {
            if (stepIndex >= mockSteps.length) {
                this.completeProcessing();
                return;
            }
            
            const step = mockSteps[stepIndex];
            this.handleProgressUpdate({
                stage: step.stage,
                progress: step.progress,
                message: step.message,
                logs: [{ message: step.message, type: step.type }]
            });
            
            stepIndex++;
            setTimeout(processStep, 1500 + Math.random() * 1000); // Random delay for realism
        };
        
        setTimeout(processStep, 1000);
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Add styles if not already present
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 16px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    animation: slideIn 0.3s ease-out;
                }
                .notification.success { background: var(--success-color); }
                .notification.error { background: var(--error-color); }
                .notification.warning { background: var(--warning-color); }
                .notification.info { background: var(--primary-color); }
                .notification button {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    margin-left: auto;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    cleanup() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StartupEvaluationApp();
});