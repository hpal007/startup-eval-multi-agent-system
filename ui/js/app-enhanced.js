/**
 * Enhanced Startup Evaluation System - Frontend Application
 * Based on ADK fullstack tutorial patterns
 * 
 * This application provides a web interface for the multi-agent startup evaluation system
 * with robust ADK integration, smart endpoint routing, and proper error handling.
 */

// Import our new ADK services
import configManager, { getConfig, getAppName } from './config.js';
import { createSession } from './session-service.js';
import StreamingConnectionManager from './streaming-manager.js';
import { checkBackendHealth, retryWithBackoff, getBackendStatus } from './health-service.js';
import deploymentManager from './deployment-strategy.js';

class EnhancedStartupEvaluationApp {
    constructor() {
        this.currentSection = 'upload';
        this.processingStage = 0;
        this.logsPaused = false;
        this.markdownRenderer = null;
        this.sessionId = null;
        this.userId = `user_${Date.now()}`;
        this.streamingManager = null;
        this.backendHealthy = false;
        
        this.stages = [
            { id: 'stage1', name: 'PDF Processing', description: 'Extracting content from document' },
            { id: 'stage2', name: 'Founder Analysis', description: 'Verifying founder backgrounds' },
            { id: 'stage3', name: 'Competitive Analysis', description: 'Researching market positioning' },
            { id: 'stage4', name: 'KPI Validation', description: 'Analyzing business metrics' }
        ];
        
        this.init();
    }
    
    async init() {
        this.initMarkdownRenderer();
        this.bindEventListeners();
        this.initializeTimestamp();
        
        // Initialize ADK services
        await this.initializeServices();
        
        // Check backend health on startup
        await this.performInitialHealthCheck();
    }

    async initializeServices() {
        try {
            console.log('🚀 [APP] Initializing ADK services...');
            
            // Initialize streaming manager with retry logic
            this.streamingManager = new StreamingConnectionManager({
                retryFn: retryWithBackoff,
                endpoint: '/run_sse'
            });

            // Log deployment configuration
            const deploymentInfo = deploymentManager.getDeploymentInfo();
            console.log('🔧 [APP] Deployment configuration:', deploymentInfo);
            
            this.addLogEntry(`Initialized ${deploymentInfo.type} deployment`, 'system');
            
            if (!deploymentInfo.validation.isValid) {
                this.addLogEntry(`Configuration warning: ${deploymentInfo.validation.error}`, 'warning');
            }

        } catch (error) {
            console.error('❌ [APP] Failed to initialize services:', error);
            this.addLogEntry('Failed to initialize ADK services: ' + error.message, 'error');
        }
    }

    async performInitialHealthCheck() {
        try {
            console.log('🔍 [APP] Performing initial health check...');
            this.addLogEntry('Checking backend connectivity...', 'system');
            
            const isHealthy = await checkBackendHealth();
            this.backendHealthy = isHealthy;
            
            if (isHealthy) {
                this.addLogEntry('✅ Backend is healthy and ready', 'success');
                
                // Test deployment configuration
                const testResult = await deploymentManager.testDeployment();
                if (testResult.success) {
                    this.addLogEntry(`✅ ${testResult.deploymentType} deployment test passed`, 'success');
                } else {
                    this.addLogEntry(`⚠️ Deployment test failed: ${testResult.error}`, 'warning');
                }
            } else {
                this.addLogEntry('❌ Backend health check failed', 'error');
                this.addLogEntry('Some features may not work properly', 'warning');
            }
        } catch (error) {
            console.error('❌ [APP] Health check error:', error);
            this.addLogEntry('Health check failed: ' + error.message, 'error');
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

        // Check backend health before processing
        if (!this.backendHealthy) {
            this.addLogEntry('Backend health check before processing...', 'system');
            const isHealthy = await checkBackendHealth();
            if (!isHealthy) {
                this.showNotification('Backend is not available. Please try again later.', 'error');
                return;
            }
            this.backendHealthy = true;
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
            
            // Create or get session using proper ADK session management
            await this.initializeSession();
            
            // Start enhanced agent processing with proper error handling
            await this.startEnhancedAgentProcessing(uploadResult);
            
        } catch (error) {
            console.error('Processing setup error:', error);
            console.error('Error details:', error.stack);
            this.addLogEntry('Failed to start processing: ' + error.message, 'error');
            
            // Use retry logic for transient errors
            if (error.message.includes('network') || error.message.includes('timeout')) {
                this.addLogEntry('Retrying with exponential backoff...', 'warning');
                try {
                    await retryWithBackoff(async () => {
                        const retryUploadResult = await this.uploadFileToServer(file);
                        await this.startEnhancedAgentProcessing(retryUploadResult);
                    });
                } catch (retryError) {
                    this.addLogEntry('Retry failed, falling back to demo mode', 'error');
                    this.startMockProcessing();
                }
            } else {
                this.addLogEntry('Falling back to demo mode for now...', 'warning');
                this.startMockProcessing();
            }
        }
    }

    async initializeSession() {
        try {
            if (!this.sessionId) {
                this.addLogEntry('Creating new session...', 'system');
                
                const sessionResult = await createSession(this.userId);
                
                if (sessionResult.success) {
                    this.sessionId = sessionResult.sessionId;
                    this.addLogEntry(`✅ Session created: ${this.sessionId}`, 'success');
                    console.log('📝 [APP] Session info:', sessionResult);
                } else {
                    this.addLogEntry(`⚠️ Session creation warning: ${sessionResult.error}`, 'warning');
                    // For Agent Engine, sessions are auto-created, so this is okay
                    this.sessionId = sessionResult.sessionId || `session_${Date.now()}`;
                }
            }
        } catch (error) {
            console.error('❌ [APP] Session initialization error:', error);
            this.addLogEntry('Session initialization failed, using fallback', 'warning');
            this.sessionId = `session_${Date.now()}`;
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

    async startEnhancedAgentProcessing(uploadResult) {
        try {
            this.addLogEntry('🚀 Starting enhanced agent processing...', 'system');
            
            // Create agent request with proper ADK format
            const requestData = {
                message: `Please analyze this startup pitch PDF file: ${uploadResult.filename}. The file is located at: ${uploadResult.file_path}`,
                userId: this.userId,
                sessionId: this.sessionId
            };

            console.log('📤 [APP] Sending request:', requestData);

            // Create callbacks for streaming updates
            const callbacks = {
                onMessageUpdate: this.handleMessageUpdate.bind(this),
                onEventUpdate: this.handleEventUpdate.bind(this),
                onWebsiteCountUpdate: this.handleWebsiteCountUpdate.bind(this)
            };

            // References for streaming state
            const accumulatedTextRef = { current: '' };
            const currentAgentRef = { current: '' };

            // Use the enhanced streaming manager
            await this.streamingManager.submitMessage(
                requestData,
                callbacks,
                accumulatedTextRef,
                currentAgentRef,
                (agent) => {
                    console.log('👤 [APP] Current agent:', agent);
                    this.updateCurrentAgent(agent);
                },
                (loading) => {
                    console.log('⏳ [APP] Loading state:', loading);
                    this.updateLoadingState(loading);
                },
                `ai_msg_${Date.now()}`
            );

            this.addLogEntry('✅ Agent processing completed successfully', 'success');
            
        } catch (error) {
            console.error('❌ [APP] Enhanced agent processing error:', error);
            this.addLogEntry('Enhanced processing failed: ' + error.message, 'error');
            throw error;
        }
    }

    handleMessageUpdate(message) {
        console.log('💬 [APP] Message update:', message);
        
        // Update progress based on message content
        if (message.text) {
            const textLength = message.text.length;
            const progress = Math.min(Math.floor(textLength / 10), 95); // Cap at 95% until complete
            this.updateProgress(progress, 'Processing...');
        }

        // Add message to logs
        if (message.isComplete) {
            this.addLogEntry('✅ Response completed', 'success');
            this.handleProcessingComplete(message.text);
        } else if (message.isError) {
            this.addLogEntry(`❌ Error: ${message.text}`, 'error');
        } else {
            this.addLogEntry(`💬 ${message.agent || 'Agent'}: ${message.text.substring(0, 100)}...`, 'info');
        }
    }

    handleEventUpdate(messageId, event) {
        console.log('🎯 [APP] Event update:', event);
        
        // Update processing stage based on event
        if (event.type === 'function_call') {
            this.addLogEntry(`🔧 ${event.title}`, 'system');
            this.updateStageFromEvent(event);
        } else if (event.type === 'function_response') {
            this.addLogEntry(`📋 ${event.title}`, 'success');
        } else if (event.type === 'thought') {
            this.addLogEntry(`💭 ${event.title}`, 'info');
        }
    }

    handleWebsiteCountUpdate(count) {
        console.log('🌐 [APP] Website count update:', count);
        // This could be displayed in the UI if needed
    }

    updateCurrentAgent(agent) {
        // Update UI to show current agent
        const progressStage = document.getElementById('progressStage');
        if (progressStage) {
            progressStage.textContent = `Current: ${agent}`;
        }
    }

    updateLoadingState(loading) {
        // Update UI loading indicators
        const progressFill = document.getElementById('progressFill');
        if (progressFill && loading) {
            progressFill.classList.add('loading-animation');
        } else if (progressFill) {
            progressFill.classList.remove('loading-animation');
        }
    }

    updateStageFromEvent(event) {
        // Map events to processing stages
        const eventToStage = {
            'process_pdf': 0,
            'pdf': 0,
            'founder': 1, 
            'competitive': 2,
            'kpi': 3
        };

        for (const [keyword, stage] of Object.entries(eventToStage)) {
            if (event.title.toLowerCase().includes(keyword) || 
                (event.metadata && JSON.stringify(event.metadata).toLowerCase().includes(keyword))) {
                if (stage !== this.processingStage) {
                    this.updateStage(stage);
                }
                break;
            }
        }
    }

    handleProcessingComplete(finalText) {
        // Mark as completed
        this.updateProgress(100, 'Analysis completed successfully!');
        this.updateStage(4);
        
        // Process results from the final text
        this.processResults(finalText);
        
        // Switch to results view after a short delay
        setTimeout(() => {
            this.switchSection('results');
        }, 2000);
    }

    processResults(resultsText) {
        try {
            // Try to parse as JSON first
            const results = JSON.parse(resultsText);
            this.displayResults(results);
        } catch (e) {
            // If not JSON, treat as markdown/text
            this.displayTextResults(resultsText);
        }
    }

    displayTextResults(text) {
        // Display text results in all tabs
        const tabs = ['executive', 'founders', 'competitors', 'kpis', 'full'];
        
        tabs.forEach(tab => {
            const element = document.getElementById(`${tab}Content`);
            if (element) {
                if (tab === 'full') {
                    element.innerHTML = this.markdownRenderer.render(text);
                } else {
                    // For other tabs, show a relevant excerpt or placeholder
                    element.innerHTML = this.markdownRenderer.render(`# ${tab.charAt(0).toUpperCase() + tab.slice(1)} Analysis\n\n*Analysis results will appear here as the system processes your startup pitch.*\n\n---\n\n${text.substring(0, 500)}...`);
                }
            }
        });
    }
    
    updateProgress(percent, stage) {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressStage = document.getElementById('progressStage');
        
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (progressPercent) progressPercent.textContent = `${Math.round(percent)}%`;
        if (progressStage) progressStage.textContent = stage;
    }
    
    updateStage(stageIndex) {
        // Mark previous stages as completed
        for (let i = 0; i < stageIndex; i++) {
            const stageElement = document.getElementById(this.stages[i].id);
            if (stageElement) {
                stageElement.classList.remove('active');
                stageElement.classList.add('completed');
                const status = stageElement.querySelector('.stage-status');
                if (status) {
                    status.textContent = 'Completed';
                    status.className = 'stage-status completed';
                }
            }
        }
        
        // Mark current stage as active
        if (stageIndex < this.stages.length) {
            const currentStage = document.getElementById(this.stages[stageIndex].id);
            if (currentStage) {
                currentStage.classList.add('active');
                const status = currentStage.querySelector('.stage-status');
                if (status) {
                    status.textContent = 'Processing';
                    status.className = 'stage-status active';
                }
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
        if (button) {
            button.textContent = this.logsPaused ? 'Resume' : 'Pause';
        }
    }
    
    clearLogs() {
        const logsContent = document.getElementById('logsContent');
        if (logsContent) {
            logsContent.innerHTML = '';
            this.addLogEntry('Logs cleared', 'system');
        }
    }

    displayResults(results) {
        const tabs = ['executive', 'founders', 'competitors', 'kpis'];
        
        tabs.forEach(tab => {
            const content = results[tab] || results[`${tab}_summary`] || `# ${tab.charAt(0).toUpperCase() + tab.slice(1)} Analysis\n\nAnalysis results will appear here.`;
            const element = document.getElementById(`${tab}Content`);
            if (element && content) {
                element.innerHTML = this.markdownRenderer.render(content);
            }
        });
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
        const tabContent = document.getElementById(`tab-${tabName}`);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    }
    
    switchSection(sectionName) {
        // Hide all sections
        const sections = ['uploadSection', 'processingSection', 'resultsSection'];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
        
        // Show target section
        const targetSection = document.getElementById(`${sectionName}Section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
        
        this.currentSection = sectionName;
        
        // Add fade-in animation
        if (targetSection) {
            targetSection.classList.add('fade-in');
            setTimeout(() => {
                targetSection.classList.remove('fade-in');
            }, 500);
        }
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
        this.userId = `user_${Date.now()}`;
        
        // Clean up streaming manager
        if (this.streamingManager) {
            this.streamingManager.cleanup();
        }
        
        this.processingStage = 0;
        this.logsPaused = false;
        
        // Reset form
        const fileInput = document.getElementById('fileInput');
        const selectedFile = document.getElementById('selectedFile');
        const submitButton = document.getElementById('submitButton');
        
        if (fileInput) fileInput.value = '';
        if (selectedFile) selectedFile.style.display = 'none';
        if (submitButton) submitButton.disabled = true;
        
        // Reset progress
        this.updateProgress(0, 'Initializing...');
        
        // Reset stages
        this.stages.forEach((stage, index) => {
            const stageElement = document.getElementById(stage.id);
            if (stageElement) {
                stageElement.classList.remove('active', 'completed');
                const status = stageElement.querySelector('.stage-status');
                if (status) {
                    status.textContent = 'Pending';
                    status.className = 'stage-status pending';
                }
            }
        });
        
        // Clear logs
        this.clearLogs();
        
        // Switch back to upload section
        this.switchSection('upload');

        // Re-check backend health
        this.performInitialHealthCheck();
    }
    
    startMockProcessing() {
        // Simulate the processing workflow for demo purposes
        this.addLogEntry('Starting mock processing for demonstration', 'system');
        
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
                this.handleProcessingComplete('Demo processing completed successfully!');
                return;
            }
            
            const step = mockSteps[stepIndex];
            this.updateProgress(step.progress, step.message);
            this.updateStage(step.stage);
            this.addLogEntry(step.message, step.type);
            
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
                .notification.success { background: var(--success-color, #10b981); }
                .notification.error { background: var(--error-color, #ef4444); }
                .notification.warning { background: var(--warning-color, #f59e0b); }
                .notification.info { background: var(--primary-color, #3b82f6); }
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
        if (this.streamingManager) {
            this.streamingManager.cleanup();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Enhanced Startup Evaluation App...');
    new EnhancedStartupEvaluationApp();
});

// Service Worker registration for offline capability (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export for debugging
window.ADKApp = { configManager, deploymentManager };