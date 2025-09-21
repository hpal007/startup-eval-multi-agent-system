/**
 * Deployment Strategy Handler
 * Based on ADK fullstack tutorial patterns
 * 
 * Implements strategy pattern for handling both local ADK backend and Agent Engine deployments,
 * providing unified interface for different deployment types.
 */

import { getEndpointForPath, getAuthHeaders, shouldUseAgentEngine, getAppName, getConfig } from './config.js';

/**
 * Abstract base class for deployment strategies
 */
class DeploymentStrategy {
    constructor() {
        if (this.constructor === DeploymentStrategy) {
            throw new Error('DeploymentStrategy is abstract and cannot be instantiated');
        }
    }

    /**
     * Format request payload for the specific deployment
     * @param {Object} requestData - Raw request data
     * @returns {Object} Formatted payload
     */
    formatPayload(requestData) {
        throw new Error('formatPayload must be implemented by subclass');
    }

    /**
     * Get the appropriate endpoint URL
     * @param {string} path - API path
     * @returns {string} Full endpoint URL
     */
    getEndpoint(path) {
        throw new Error('getEndpoint must be implemented by subclass');
    }

    /**
     * Get authentication headers
     * @returns {Promise<Object>} Headers object
     */
    async getHeaders() {
        throw new Error('getHeaders must be implemented by subclass');
    }

    /**
     * Validate the deployment configuration
     * @returns {Object} Validation result
     */
    validateConfig() {
        throw new Error('validateConfig must be implemented by subclass');
    }

    /**
     * Handle streaming request
     * @param {Object} requestData - Request data
     * @returns {Promise<Response>} Streaming response
     */
    async handleStreamRequest(requestData) {
        throw new Error('handleStreamRequest must be implemented by subclass');
    }
}

/**
 * Local Backend Deployment Strategy
 * Handles requests for local ADK backend deployment
 */
class LocalBackendStrategy extends DeploymentStrategy {
    constructor() {
        super();
        this.deploymentType = 'local_backend';
    }

    /**
     * Format payload for local backend
     */
    formatPayload(requestData) {
        return {
            appName: getAppName(),
            userId: requestData.userId,
            sessionId: requestData.sessionId,
            newMessage: {
                parts: [{ text: requestData.message }],
                role: 'user',
            },
            streaming: true,
        };
    }

    /**
     * Get local backend endpoint
     */
    getEndpoint(path) {
        return getEndpointForPath(path);
    }

    /**
     * Get authentication headers for local backend
     */
    async getHeaders() {
        const baseHeaders = await getAuthHeaders();
        return {
            ...baseHeaders,
            'Accept': 'text/event-stream',
        };
    }

    /**
     * Validate local backend configuration
     */
    validateConfig() {
        const config = getConfig();
        
        if (config.deploymentType !== 'local_backend') {
            return {
                isValid: false,
                error: 'Configuration mismatch: expected local_backend'
            };
        }

        // Check if we can reach the local backend
        const endpoint = this.getEndpoint('/health');
        if (!endpoint.includes('localhost') && !endpoint.includes('127.0.0.1')) {
            return {
                isValid: false,
                error: 'Local backend endpoint does not appear to be local'
            };
        }

        return { isValid: true };
    }

    /**
     * Handle streaming request for local backend
     */
    async handleStreamRequest(requestData) {
        try {
            const payload = this.formatPayload(requestData);
            const url = this.getEndpoint('/run_sse');
            const headers = await this.getHeaders();

            console.log('🔗 [LOCAL BACKEND] Sending request:', { url, payload });

            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Local backend error: ${response.status} ${errorText}`);
            }

            console.log('✅ [LOCAL BACKEND] Streaming response received');
            return response;
        } catch (error) {
            console.error('❌ [LOCAL BACKEND] Request failed:', error);
            throw error;
        }
    }
}

/**
 * Agent Engine Deployment Strategy  
 * Handles requests for Agent Engine deployment
 */
class AgentEngineStrategy extends DeploymentStrategy {
    constructor() {
        super();
        this.deploymentType = 'agent_engine';
    }

    /**
     * Format payload for Agent Engine
     */
    formatPayload(requestData) {
        return {
            class_method: 'stream_query',
            input: {
                user_id: requestData.userId,
                session_id: requestData.sessionId,
                message: requestData.message,
            },
        };
    }

    /**
     * Get Agent Engine endpoint
     */
    getEndpoint(path) {
        return getEndpointForPath(path);
    }

    /**
     * Get authentication headers for Agent Engine
     */
    async getHeaders() {
        const baseHeaders = await getAuthHeaders();
        return {
            ...baseHeaders,
            'Accept': 'text/event-stream',
        };
    }

    /**
     * Validate Agent Engine configuration
     */
    validateConfig() {
        const config = getConfig();
        
        if (config.deploymentType !== 'agent_engine') {
            return {
                isValid: false,
                error: 'Configuration mismatch: expected agent_engine'
            };
        }

        // Check if Agent Engine endpoint is configured
        if (!config.baseEndpoint.includes('aiplatform.googleapis.com')) {
            return {
                isValid: false,
                error: 'Agent Engine endpoint does not appear to be a valid Google AI Platform URL'
            };
        }

        return { isValid: true };
    }

    /**
     * Handle streaming request for Agent Engine
     */
    async handleStreamRequest(requestData) {
        try {
            const payload = this.formatPayload(requestData);
            const url = this.getEndpoint('/run_sse');
            const headers = await this.getHeaders();

            console.log('🔗 [AGENT ENGINE] Sending request:', { url, payload });

            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Agent Engine error: ${response.status} ${errorText}`);
            }

            console.log('✅ [AGENT ENGINE] Streaming response received');
            return response;
        } catch (error) {
            console.error('❌ [AGENT ENGINE] Request failed:', error);
            throw error;
        }
    }
}

/**
 * Cloud Run Deployment Strategy
 * Handles requests for Cloud Run deployment (ADK backend on Cloud Run)
 */
class CloudRunStrategy extends LocalBackendStrategy {
    constructor() {
        super();
        this.deploymentType = 'cloud_run';
    }

    /**
     * Validate Cloud Run configuration
     */
    validateConfig() {
        const config = getConfig();
        
        if (config.deploymentType !== 'cloud_run') {
            return {
                isValid: false,
                error: 'Configuration mismatch: expected cloud_run'
            };
        }

        // Check if Cloud Run endpoint is configured
        if (!config.baseEndpoint.includes('.run.app')) {
            return {
                isValid: false,
                error: 'Cloud Run endpoint does not appear to be a valid Cloud Run URL'
            };
        }

        return { isValid: true };
    }
}

/**
 * Deployment Strategy Factory
 * Creates appropriate strategy based on configuration
 */
class DeploymentStrategyFactory {
    /**
     * Create strategy based on current configuration
     * @returns {DeploymentStrategy} Appropriate strategy instance
     */
    static createStrategy() {
        const config = getConfig();
        
        switch (config.deploymentType) {
            case 'agent_engine':
                console.log('🎯 [STRATEGY] Using Agent Engine strategy');
                return new AgentEngineStrategy();
            
            case 'cloud_run':
                console.log('🎯 [STRATEGY] Using Cloud Run strategy');
                return new CloudRunStrategy();
            
            case 'local_backend':
            default:
                console.log('🎯 [STRATEGY] Using Local Backend strategy');
                return new LocalBackendStrategy();
        }
    }

    /**
     * Get strategy for specific deployment type
     * @param {string} deploymentType - Type of deployment
     * @returns {DeploymentStrategy} Strategy instance
     */
    static getStrategy(deploymentType) {
        switch (deploymentType) {
            case 'agent_engine':
                return new AgentEngineStrategy();
            case 'cloud_run':
                return new CloudRunStrategy();
            case 'local_backend':
                return new LocalBackendStrategy();
            default:
                throw new Error(`Unknown deployment type: ${deploymentType}`);
        }
    }
}

/**
 * Deployment Manager
 * High-level interface for deployment operations
 */
export class DeploymentManager {
    constructor() {
        this.currentStrategy = DeploymentStrategyFactory.createStrategy();
        this.config = getConfig();
    }

    /**
     * Get current deployment information
     * @returns {Object} Deployment info
     */
    getDeploymentInfo() {
        return {
            type: this.currentStrategy.deploymentType,
            config: this.config,
            validation: this.currentStrategy.validateConfig()
        };
    }

    /**
     * Handle streaming request with current strategy
     * @param {Object} requestData - Request data
     * @returns {Promise<Response>} Streaming response
     */
    async handleStreamRequest(requestData) {
        const validation = this.currentStrategy.validateConfig();
        if (!validation.isValid) {
            throw new Error(`Configuration validation failed: ${validation.error}`);
        }

        return await this.currentStrategy.handleStreamRequest(requestData);
    }

    /**
     * Switch to a different deployment strategy
     * @param {string} deploymentType - New deployment type
     */
    switchStrategy(deploymentType) {
        console.log(`🔄 [DEPLOYMENT] Switching from ${this.currentStrategy.deploymentType} to ${deploymentType}`);
        this.currentStrategy = DeploymentStrategyFactory.getStrategy(deploymentType);
    }

    /**
     * Test the current deployment
     * @returns {Promise<Object>} Test result
     */
    async testDeployment() {
        const validation = this.currentStrategy.validateConfig();
        if (!validation.isValid) {
            return {
                success: false,
                error: validation.error,
                deploymentType: this.currentStrategy.deploymentType
            };
        }

        try {
            // Test with a simple health check
            const endpoint = this.currentStrategy.getEndpoint('/health');
            const headers = await this.currentStrategy.getHeaders();
            
            const response = await fetch(endpoint, {
                method: 'GET',
                headers,
                signal: AbortSignal.timeout(5000)
            });

            return {
                success: response.ok,
                status: response.status,
                statusText: response.statusText,
                deploymentType: this.currentStrategy.deploymentType,
                endpoint
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                deploymentType: this.currentStrategy.deploymentType
            };
        }
    }
}

// Export strategy classes
export { DeploymentStrategy, LocalBackendStrategy, AgentEngineStrategy, CloudRunStrategy };

// Export factory
export { DeploymentStrategyFactory };

// Create and export singleton manager
const deploymentManager = new DeploymentManager();
export default deploymentManager;

// Export convenience functions
export const getDeploymentInfo = () => deploymentManager.getDeploymentInfo();
export const handleStreamRequest = (requestData) => deploymentManager.handleStreamRequest(requestData);
export const testDeployment = () => deploymentManager.testDeployment();