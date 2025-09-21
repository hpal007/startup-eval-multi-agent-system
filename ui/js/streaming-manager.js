/**
 * Streaming Connection Manager
 * Based on ADK fullstack tutorial patterns
 * 
 * Manages SSE streaming connections with proper error handling, retry logic,
 * and real-time processing capabilities for both local backend and Agent Engine.
 */

import { getEndpointForPath, getAuthHeaders, shouldUseAgentEngine, getAppName } from './config.js';

/**
 * SSE Connection States
 */
export const SSEConnectionState = {
    IDLE: 'idle',
    CONNECTING: 'connecting', 
    CONNECTED: 'connected',
    ERROR: 'error',
    CLOSED: 'closed'
};

/**
 * Streaming Connection Manager
 * Handles SSE streaming connections with robust error handling and retry logic
 */
export class StreamingConnectionManager {
    constructor(options = {}) {
        this.connectionState = SSEConnectionState.IDLE;
        this.retryFn = options.retryFn || ((fn) => fn());
        this.endpoint = options.endpoint || '/run_sse';
        this.abortController = null;
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
    }

    /**
     * Get the current connection state
     */
    getConnectionState() {
        return this.connectionState;
    }

    /**
     * Submit a message and start streaming
     * @param {Object} apiPayload - API request payload
     * @param {Object} callbacks - Stream processing callbacks
     * @param {Object} accumulatedTextRef - Reference to accumulated text
     * @param {Object} currentAgentRef - Reference to current agent state
     * @param {Function} setCurrentAgent - Agent state setter
     * @param {Function} setIsLoading - Loading state setter
     * @param {string} aiMessageId - AI message identifier
     */
    async submitMessage(apiPayload, callbacks, accumulatedTextRef, currentAgentRef, setCurrentAgent, setIsLoading, aiMessageId) {
        try {
            this.connectionState = SSEConnectionState.CONNECTING;
            setIsLoading(true);

            // Reset accumulated text
            accumulatedTextRef.current = '';

            // Create abort controller for cancellation
            this.abortController = new AbortController();

            console.log('🔗 [STREAMING] Starting stream with payload:', apiPayload);

            // Get appropriate endpoint
            const streamEndpoint = getEndpointForPath(this.endpoint);
            const authHeaders = await getAuthHeaders();

            // Make the streaming request
            const response = await fetch(streamEndpoint, {
                method: 'POST',
                headers: {
                    ...authHeaders,
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify(apiPayload),
                signal: this.abortController.signal
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            this.connectionState = SSEConnectionState.CONNECTED;

            // Handle SSE streaming with proper event processing
            await this.handleSSEStream(
                response,
                aiMessageId,
                callbacks,
                accumulatedTextRef,
                currentAgentRef,
                setCurrentAgent
            );

            this.connectionState = SSEConnectionState.IDLE;
            setIsLoading(false);
        } catch (error) {
            if (error.name === 'AbortError') {
                this.connectionState = SSEConnectionState.CLOSED;
                console.log('🛑 [STREAMING] Request was cancelled by the user');
            } else {
                this.connectionState = SSEConnectionState.ERROR;
                console.error('❌ [STREAMING] Error during streaming:', error);
                throw error;
            }
            setIsLoading(false);
        }
    }

    /**
     * Handle SSE streaming from the response
     * @param {Response} response - Fetch response with SSE stream
     * @param {string} aiMessageId - AI message ID for updates
     * @param {Object} callbacks - Stream processing callbacks
     * @param {Object} accumulatedTextRef - Reference to accumulated text
     * @param {Object} currentAgentRef - Reference to current agent state
     * @param {Function} setCurrentAgent - Agent state setter
     */
    async handleSSEStream(response, aiMessageId, callbacks, accumulatedTextRef, currentAgentRef, setCurrentAgent) {
        const contentType = response.headers.get('content-type') || '';
        
        console.log('📡 [STREAMING] Processing response as SSE, Content-Type:', contentType);

        // Handle SSE streaming response
        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('No readable stream available');
        }

        const decoder = new TextDecoder();
        let lineBuffer = '';
        let eventDataBuffer = '';

        console.log('🎯 [STREAMING] Beginning to process streaming response');

        const pump = async () => {
            const { value, done } = await reader.read();

            if (value) {
                const chunk = decoder.decode(value, { stream: true });
                lineBuffer += chunk;

                // Process complete lines
                const lines = lineBuffer.split('\n');
                lineBuffer = lines.pop() || ''; // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line === '') {
                        // Empty line signals end of event
                        if (eventDataBuffer.length > 0) {
                            const jsonDataToParse = eventDataBuffer.endsWith('\n')
                                ? eventDataBuffer.slice(0, -1)
                                : eventDataBuffer;

                            console.log('📨 [STREAMING] Processing SSE event:', 
                                jsonDataToParse.substring(0, 200) + '...'
                            );

                            // Process the event immediately for real-time updates
                            try {
                                await this.processSseEventData(
                                    jsonDataToParse,
                                    aiMessageId,
                                    callbacks,
                                    accumulatedTextRef,
                                    currentAgentRef,
                                    setCurrentAgent
                                );

                                // Force immediate UI update by yielding to event loop
                                await new Promise((resolve) => setTimeout(resolve, 0));
                            } catch (error) {
                                console.error('❌ [STREAMING] Failed to process SSE event:', error);
                            }
                            eventDataBuffer = ''; // Reset for next event
                        }
                    } else if (line.startsWith('data:')) {
                        // Accumulate data lines for this event
                        eventDataBuffer += line.substring(5).trimStart() + '\n';
                        console.log('📝 [STREAMING] Added to buffer:', line.substring(5).trimStart());
                    } else if (line.startsWith(':')) {
                        console.log('💬 [STREAMING] Ignoring comment:', line);
                    }
                }
            }

            if (done) {
                // Handle any remaining data in buffer
                if (eventDataBuffer.length > 0) {
                    const jsonDataToParse = eventDataBuffer.endsWith('\n')
                        ? eventDataBuffer.slice(0, -1)
                        : eventDataBuffer;

                    console.log('🔚 [STREAMING] Processing final event:', 
                        jsonDataToParse.substring(0, 200) + '...'
                    );

                    try {
                        await this.processSseEventData(
                            jsonDataToParse,
                            aiMessageId,
                            callbacks,
                            accumulatedTextRef,
                            currentAgentRef,
                            setCurrentAgent
                        );
                    } catch (error) {
                        console.error('❌ [STREAMING] Failed to process final event:', error);
                    }
                }
                return;
            }

            // Continue processing next chunk
            return pump();
        };

        try {
            await pump();
        } catch (error) {
            console.error('❌ [STREAMING] Error reading stream:', error);
            throw error;
        }
    }

    /**
     * Process SSE event data and trigger appropriate callbacks
     * @param {string} jsonData - Raw SSE JSON data string
     * @param {string} aiMessageId - AI message ID for updates
     * @param {Object} callbacks - Stream processing callbacks
     * @param {Object} accumulatedTextRef - Reference to accumulated text
     * @param {Object} currentAgentRef - Reference to current agent state
     * @param {Function} setCurrentAgent - Agent state setter
     */
    async processSseEventData(jsonData, aiMessageId, callbacks, accumulatedTextRef, currentAgentRef, setCurrentAgent) {
        try {
            const parsedData = JSON.parse(jsonData);
            console.log('🔍 [STREAMING] Parsed SSE data:', parsedData);

            // Extract agent information
            const agent = parsedData.author || 'startup-evaluator';
            if (agent !== currentAgentRef.current) {
                currentAgentRef.current = agent;
                setCurrentAgent(agent);
            }

            // Handle different types of content
            if (parsedData.content && parsedData.content.parts) {
                for (const part of parsedData.content.parts) {
                    if (part.text) {
                        // Handle text content
                        accumulatedTextRef.current += part.text;
                        
                        // Update message with accumulated text
                        callbacks.onMessageUpdate({
                            id: aiMessageId,
                            text: accumulatedTextRef.current,
                            sender: 'assistant',
                            timestamp: new Date(),
                            agent: agent,
                            isComplete: false
                        });
                    }

                    if (part.thought) {
                        // Handle thought/reasoning content
                        console.log('💭 [STREAMING] Processing thought:', part);
                        
                        // Create timeline event for the thought
                        const event = {
                            id: `thought_${Date.now()}`,
                            type: 'thought',
                            agent: agent,
                            title: `${agent} is thinking...`,
                            timestamp: new Date(),
                            metadata: { thought: true }
                        };

                        callbacks.onEventUpdate(aiMessageId, event);
                    }

                    if (part.function_call) {
                        // Handle function/tool calls
                        console.log('🔧 [STREAMING] Processing function call:', part.function_call);
                        
                        const event = {
                            id: `function_${part.function_call.id || Date.now()}`,
                            type: 'function_call',
                            agent: agent,
                            title: `Calling ${part.function_call.name}`,
                            timestamp: new Date(),
                            metadata: { function_call: part.function_call }
                        };

                        callbacks.onEventUpdate(aiMessageId, event);
                    }

                    if (part.function_response) {
                        // Handle function/tool responses
                        console.log('📋 [STREAMING] Processing function response:', part.function_response);
                        
                        const event = {
                            id: `response_${part.function_response.id || Date.now()}`,
                            type: 'function_response',
                            agent: agent,
                            title: `${part.function_response.name} completed`,
                            timestamp: new Date(),
                            metadata: { function_response: part.function_response }
                        };

                        callbacks.onEventUpdate(aiMessageId, event);
                    }
                }
            }

            // Handle completion signals
            if (parsedData.turnComplete || parsedData.complete) {
                console.log('✅ [STREAMING] Stream completed');
                
                // Mark message as complete
                callbacks.onMessageUpdate({
                    id: aiMessageId,
                    text: accumulatedTextRef.current,
                    sender: 'assistant',
                    timestamp: new Date(),
                    agent: agent,
                    isComplete: true
                });
            }

            // Handle errors
            if (parsedData.error || parsedData.errorMessage) {
                const errorMessage = parsedData.error || parsedData.errorMessage;
                console.error('❌ [STREAMING] Received error from stream:', errorMessage);
                
                callbacks.onMessageUpdate({
                    id: aiMessageId,
                    text: `Error: ${errorMessage}`,
                    sender: 'assistant',
                    timestamp: new Date(),
                    agent: 'error',
                    isComplete: true,
                    isError: true
                });
            }

        } catch (error) {
            console.error('❌ [STREAMING] Failed to parse SSE JSON:', error);
            console.error('❌ [STREAMING] Problematic JSON:', jsonData.substring(0, 500));
        }
    }

    /**
     * Cancel the current streaming connection
     */
    cancelStream() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
            this.connectionState = SSEConnectionState.CLOSED;
        }
    }

    /**
     * Clean up resources
     */
    cleanup() {
        this.cancelStream();
    }
}

export default StreamingConnectionManager;