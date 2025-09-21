/**
 * Health Check Service
 * Based on ADK fullstack tutorial patterns
 * 
 * Provides backend health checking with retry logic and proper error handling.
 */

import { getEndpointForPath, getAuthHeaders } from './config.js';

/**
 * Health Check Service
 * Handles backend connectivity validation and health monitoring
 */
export class HealthCheckService {
    constructor(options = {}) {
        this.maxRetries = options.maxRetries || 10;
        this.retryDelay = options.retryDelay || 2000;
        this.timeout = options.timeout || 10000;
        this.healthEndpoint = options.healthEndpoint || '/health';
    }

    /**
     * Check if the backend is healthy
     * @returns {Promise<boolean>} True if backend is healthy
     */
    async checkBackendHealth() {
        try {
            const healthUrl = getEndpointForPath(this.healthEndpoint);
            const authHeaders = await getAuthHeaders();

            console.log('🔍 [HEALTH CHECK] Checking backend health:', healthUrl);

            const response = await fetch(healthUrl, {
                method: 'GET',
                headers: {
                    ...authHeaders,
                    'Accept': 'application/json',
                },
                signal: AbortSignal.timeout(this.timeout)
            });

            const isHealthy = response.ok;
            
            if (isHealthy) {
                console.log('✅ [HEALTH CHECK] Backend is healthy');
                try {
                    const healthData = await response.json();
                    console.log('📊 [HEALTH CHECK] Health data:', healthData);
                } catch (e) {
                    // Health endpoint might not return JSON, that's okay
                    console.log('💡 [HEALTH CHECK] Health endpoint returned non-JSON response');
                }
            } else {
                console.warn('⚠️ [HEALTH CHECK] Backend health check failed:', {
                    status: response.status,
                    statusText: response.statusText
                });
            }

            return isHealthy;
        } catch (error) {
            console.error('❌ [HEALTH CHECK] Backend health check error:', error);
            return false;
        }
    }

    /**
     * Wait for backend to be ready with retry logic
     * @param {number} maxAttempts - Maximum number of attempts
     * @returns {Promise<boolean>} True if backend becomes ready
     */
    async waitForBackend(maxAttempts = null) {
        const attempts = maxAttempts || this.maxRetries;
        console.log(`⏳ [HEALTH CHECK] Waiting for backend to be ready (max ${attempts} attempts)...`);

        for (let attempt = 1; attempt <= attempts; attempt++) {
            console.log(`🔄 [HEALTH CHECK] Attempt ${attempt}/${attempts}`);
            
            const isHealthy = await this.checkBackendHealth();
            if (isHealthy) {
                console.log('✅ [HEALTH CHECK] Backend is ready!');
                return true;
            }

            if (attempt < attempts) {
                console.log(`⏱️ [HEALTH CHECK] Waiting ${this.retryDelay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            }
        }

        console.error('❌ [HEALTH CHECK] Backend failed to become ready after', attempts, 'attempts');
        return false;
    }

    /**
     * Retry a function with exponential backoff
     * @param {Function} fn - Function to retry
     * @param {number} maxRetries - Maximum number of retries
     * @param {number} maxDuration - Maximum duration in milliseconds
     * @returns {Promise<any>} Result of the function
     */
    async retryWithBackoff(fn, maxRetries = null, maxDuration = 120000) {
        const retries = maxRetries || this.maxRetries;
        const startTime = Date.now();
        let lastError;

        console.log(`🔄 [RETRY] Starting retry with backoff (max ${retries} retries, ${maxDuration}ms duration)`);

        for (let attempt = 0; attempt < retries; attempt++) {
            // Check if we've exceeded the maximum duration
            if (Date.now() - startTime > maxDuration) {
                console.error(`⏰ [RETRY] Exceeded maximum duration of ${maxDuration}ms`);
                throw new Error(`Operation timed out after ${maxDuration}ms`);
            }

            try {
                console.log(`🎯 [RETRY] Attempt ${attempt + 1}/${retries}`);
                const result = await fn();
                
                if (attempt > 0) {
                    console.log(`✅ [RETRY] Success after ${attempt + 1} attempts`);
                }
                
                return result;
            } catch (error) {
                lastError = error;
                console.warn(`⚠️ [RETRY] Attempt ${attempt + 1} failed:`, error.message);

                // Don't wait after the last attempt
                if (attempt < retries - 1) {
                    // Exponential backoff: 1s, 2s, 4s, 8s, 16s (capped at 16s)
                    const delay = Math.min(1000 * Math.pow(2, attempt), 16000);
                    console.log(`⏱️ [RETRY] Waiting ${delay}ms before next attempt...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }

        console.error(`❌ [RETRY] All ${retries} attempts failed`);
        throw lastError;
    }

    /**
     * Get detailed backend status information
     * @returns {Promise<Object>} Backend status information
     */
    async getBackendStatus() {
        try {
            const healthUrl = getEndpointForPath(this.healthEndpoint);
            const authHeaders = await getAuthHeaders();

            const response = await fetch(healthUrl, {
                method: 'GET',
                headers: {
                    ...authHeaders,
                    'Accept': 'application/json',
                },
                signal: AbortSignal.timeout(this.timeout)
            });

            const status = {
                healthy: response.ok,
                status: response.status,
                statusText: response.statusText,
                timestamp: new Date().toISOString(),
                responseTime: null,
                headers: Object.fromEntries(response.headers.entries())
            };

            if (response.ok) {
                try {
                    status.data = await response.json();
                } catch (e) {
                    status.data = null;
                    status.note = 'Health endpoint returned non-JSON response';
                }
            } else {
                try {
                    status.error = await response.text();
                } catch (e) {
                    status.error = 'Failed to read error response';
                }
            }

            return status;
        } catch (error) {
            return {
                healthy: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Monitor backend health continuously
     * @param {Function} callback - Callback function to receive health status
     * @param {number} interval - Check interval in milliseconds
     * @returns {Function} Function to stop monitoring
     */
    startHealthMonitoring(callback, interval = 30000) {
        console.log(`📡 [HEALTH MONITOR] Starting health monitoring (interval: ${interval}ms)`);
        
        let isMonitoring = true;
        
        const monitor = async () => {
            if (!isMonitoring) return;
            
            const status = await this.getBackendStatus();
            callback(status);
            
            if (isMonitoring) {
                setTimeout(monitor, interval);
            }
        };

        // Start monitoring immediately
        monitor();

        // Return stop function
        return () => {
            console.log('🛑 [HEALTH MONITOR] Stopping health monitoring');
            isMonitoring = false;
        };
    }
}

// Create singleton instance
const healthCheckService = new HealthCheckService();

// Export individual functions for easy access
export const checkBackendHealth = () => healthCheckService.checkBackendHealth();
export const waitForBackend = (maxAttempts) => healthCheckService.waitForBackend(maxAttempts);
export const retryWithBackoff = (fn, maxRetries, maxDuration) => healthCheckService.retryWithBackoff(fn, maxRetries, maxDuration);
export const getBackendStatus = () => healthCheckService.getBackendStatus();
export const startHealthMonitoring = (callback, interval) => healthCheckService.startHealthMonitoring(callback, interval);

// Export the service for advanced usage
export default healthCheckService;