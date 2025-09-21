/**
 * Configuration and Environment Detection
 * Based on ADK fullstack tutorial patterns
 * 
 * This module automatically detects the deployment environment and provides
 * appropriate endpoint routing for local backend vs Agent Engine deployments.
 */

class ConfigurationManager {
    constructor() {
        this.config = this.detectEnvironment();
    }

    /**
     * Detect the current deployment environment
     * @returns {Object} Configuration object with deployment info
     */
    detectEnvironment() {
        // Check if we're in a production environment with Agent Engine
        const agentEngineEndpoint = this.getEnvVariable('AGENT_ENGINE_ENDPOINT');
        const cloudRunUrl = this.getEnvVariable('CLOUD_RUN_SERVICE_URL');
        const backendUrl = this.getEnvVariable('BACKEND_URL');

        let deploymentType = 'local_backend';
        let baseEndpoint = 'http://127.0.0.1:8080'; // Default local backend

        if (agentEngineEndpoint) {
            deploymentType = 'agent_engine';
            baseEndpoint = agentEngineEndpoint;
        } else if (cloudRunUrl) {
            deploymentType = 'cloud_run';
            baseEndpoint = cloudRunUrl;
        } else if (backendUrl) {
            deploymentType = 'local_backend';
            baseEndpoint = backendUrl;
        }

        return {
            deploymentType,
            baseEndpoint,
            appName: this.getEnvVariable('ADK_APP_NAME') || 'chatgpt_agentic_clone_app',
            isProduction: deploymentType !== 'local_backend',
            supportedFeatures: this.getSupportedFeatures(deploymentType)
        };
    }

    /**
     * Get environment variable (in browser, this would come from build-time or server)
     * For now, we'll use defaults since we can't access process.env in browser
     */
    getEnvVariable(name) {
        // In a real Next.js app, this would be process.env.NEXT_PUBLIC_*
        // For our current setup, we'll detect based on current location
        if (typeof window !== 'undefined') {
            const hostname = window.location.hostname;
            const port = window.location.port;
            
            // Local development detection
            if (hostname === 'localhost' || hostname === '127.0.0.1') {
                if (name === 'BACKEND_URL') {
                    return `http://${hostname}:${port || 8080}`;
                }
            }
        }
        return null;
    }

    /**
     * Get supported features based on deployment type
     */
    getSupportedFeatures(deploymentType) {
        const features = {
            local_backend: {
                sessions: true,
                streaming: true,
                fileUpload: true,
                healthCheck: true
            },
            agent_engine: {
                sessions: true,
                streaming: true,
                fileUpload: false, // Agent Engine typically doesn't handle file uploads directly
                healthCheck: true
            },
            cloud_run: {
                sessions: true,
                streaming: true,
                fileUpload: true,
                healthCheck: true
            }
        };

        return features[deploymentType] || features.local_backend;
    }

    /**
     * Get the appropriate endpoint for a given path
     * @param {string} path - The API path (e.g., '/run_sse', '/health')
     * @param {string} apiType - Optional API type ('sessions', 'agents', etc.)
     * @returns {string} Full endpoint URL
     */
    getEndpointForPath(path, apiType = null) {
        const { deploymentType, baseEndpoint } = this.config;

        // Handle different endpoint patterns based on deployment type
        switch (deploymentType) {
            case 'agent_engine':
                // Agent Engine uses different URL patterns
                if (apiType === 'sessions') {
                    return `${baseEndpoint}/v1beta1/sessions${path}`;
                }
                return `${baseEndpoint}${path}`;

            case 'cloud_run':
            case 'local_backend':
            default:
                // Standard API paths
                return `${baseEndpoint}${path}`;
        }
    }

    /**
     * Get authentication headers based on deployment type
     * @returns {Object} Headers object
     */
    async getAuthHeaders() {
        const { deploymentType } = this.config;

        const headers = {
            'Content-Type': 'application/json'
        };

        switch (deploymentType) {
            case 'agent_engine':
                // In production, you'd need to handle Google Cloud authentication
                // For now, we'll use the default headers
                break;
            
            case 'cloud_run':
                // Cloud Run might need specific headers
                break;
            
            case 'local_backend':
            default:
                // Local backend uses standard headers
                break;
        }

        return headers;
    }

    /**
     * Check if we should use Agent Engine
     * @returns {boolean}
     */
    shouldUseAgentEngine() {
        return this.config.deploymentType === 'agent_engine';
    }

    /**
     * Get the current configuration
     * @returns {Object}
     */
    getConfig() {
        return { ...this.config };
    }

    /**
     * Get the ADK app name
     * @returns {string}
     */
    getAppName() {
        return this.config.appName;
    }
}

// Export singleton instance
const configManager = new ConfigurationManager();

// Export individual functions for easy access
export const getEndpointForPath = (path, apiType) => configManager.getEndpointForPath(path, apiType);
export const getAuthHeaders = () => configManager.getAuthHeaders();
export const shouldUseAgentEngine = () => configManager.shouldUseAgentEngine();
export const getConfig = () => configManager.getConfig();
export const getAppName = () => configManager.getAppName();

// Export the manager for advanced usage
export default configManager;

// For debugging and development
window.adkConfig = configManager;
console.log('🔧 ADK Configuration loaded:', configManager.getConfig());