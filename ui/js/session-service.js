/**
 * ADK Session Service
 * Based on ADK fullstack tutorial patterns
 * 
 * Handles session management for both local backend and Agent Engine deployments.
 * Uses smart endpoint routing and follows ADK best practices.
 */

import { getEndpointForPath, getAuthHeaders, shouldUseAgentEngine, getAppName } from './config.js';

/**
 * ADK Session Service - Handles all session-related API calls
 * Uses smart endpoint routing to work with both local backend and Agent Engine
 */
export class AdkSessionService {
    /**
     * Create a new session
     * @param {string} userId - User identifier
     * @returns {Promise<Object>} Session creation result
     */
    static async createSession(userId) {
        const appName = getAppName();
        
        if (shouldUseAgentEngine()) {
            // Agent Engine: Sessions are created automatically during first interaction
            // We just return a session ID format that Agent Engine expects
            const sessionId = `session_${Date.now()}_${userId}`;
            console.log('🔗 [ADK SESSION SERVICE] Agent Engine auto-session:', { sessionId, userId });
            
            return {
                success: true,
                sessionId,
                created: false, // Not explicitly created, will be auto-created
                deploymentType: 'agent_engine'
            };
        } else {
            // Local Backend: Create session explicitly
            const endpoint = getEndpointForPath(`/apps/${appName}/users/${userId}/sessions`);
            
            console.log('🔗 [ADK SESSION SERVICE] Local Backend createSession request:', {
                endpoint,
                method: 'POST',
                userId,
                appName
            });

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        ...authHeaders,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('❌ [ADK SESSION SERVICE] Local Backend createSession error:', {
                        status: response.status,
                        statusText: response.statusText,
                        errorText
                    });
                    
                    return {
                        success: false,
                        error: `Session creation failed: ${response.status} ${errorText}`,
                        deploymentType: 'local_backend'
                    };
                }

                const sessionData = await response.json();
                console.log('✅ [ADK SESSION SERVICE] Local Backend createSession success:', sessionData);

                return {
                    success: true,
                    sessionId: sessionData.id,
                    created: true,
                    deploymentType: 'local_backend',
                    sessionData
                };
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Local Backend createSession error:', error);
                return {
                    success: false,
                    error: error.message,
                    deploymentType: 'local_backend'
                };
            }
        }
    }

    /**
     * Retrieve a specific session by ID
     * @param {string} userId - User identifier
     * @param {string} sessionId - Session identifier
     * @returns {Promise<Object|null>} Session data or null if not found
     */
    static async getSession(userId, sessionId) {
        const appName = getAppName();

        if (shouldUseAgentEngine()) {
            // Agent Engine: Use v1beta1 sessions API
            const endpoint = getEndpointForPath(`/${sessionId}`, 'sessions');

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                if (response.status === 404) {
                    return null;
                }

                if (!response.ok) {
                    throw new Error(`Failed to get session: ${response.statusText}`);
                }

                return response.json();
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Agent Engine getSession error:', error);
                throw error;
            }
        } else {
            // Local Backend: GET with path
            const endpoint = getEndpointForPath(`/apps/${appName}/users/${userId}/sessions/${sessionId}`);

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                if (response.status === 404) {
                    return null;
                }

                if (!response.ok) {
                    throw new Error(`Failed to get session: ${response.statusText}`);
                }

                return response.json();
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Local Backend getSession error:', error);
                throw error;
            }
        }
    }

    /**
     * List all sessions for a user
     * @param {string} userId - User identifier
     * @returns {Promise<Object>} List of sessions
     */
    static async listSessions(userId) {
        const appName = getAppName();

        if (shouldUseAgentEngine()) {
            // Agent Engine: Use v1beta1 sessions API
            const endpoint = getEndpointForPath('', 'sessions');

            console.log('🔗 [ADK SESSION SERVICE] Agent Engine listSessions request:', {
                endpoint,
                method: 'GET',
            });

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to list sessions: ${response.statusText}`);
                }

                const responseData = await response.json();
                console.log('✅ [ADK SESSION SERVICE] Agent Engine listSessions success:', {
                    sessionsCount: responseData.sessions?.length || 0
                });

                return {
                    sessions: responseData.sessions || [],
                    sessionIds: (responseData.sessions || []).map(session => session.id)
                };
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Agent Engine listSessions error:', error);
                throw error;
            }
        } else {
            // Local Backend: GET with path
            const endpoint = getEndpointForPath(`/apps/${appName}/users/${userId}/sessions`);

            console.log('🔗 [ADK SESSION SERVICE] Local Backend listSessions request:', {
                endpoint,
                method: 'GET',
                userId,
                appName,
            });

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                console.log('📡 [ADK SESSION SERVICE] Local Backend response:', {
                    status: response.status,
                    statusText: response.statusText,
                    contentType: response.headers.get('content-type'),
                });

                if (!response.ok) {
                    throw new Error(`Failed to list sessions: ${response.statusText}`);
                }

                const sessions = await response.json();

                console.log('✅ [ADK SESSION SERVICE] Local Backend success:', {
                    sessionsCount: sessions.length,
                    sessionIds: sessions.map(s => s.id || 'no-id'),
                });

                return {
                    sessions,
                    sessionIds: sessions.map(session => session.id),
                };
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Local Backend error:', error);
                throw error;
            }
        }
    }

    /**
     * List all events for a specific session
     * @param {string} userId - User identifier  
     * @param {string} sessionId - Session identifier
     * @returns {Promise<Object>} List of events
     */
    static async listEvents(userId, sessionId) {
        const appName = getAppName();

        if (shouldUseAgentEngine()) {
            // Agent Engine: Use v1beta1 sessions API for events
            const endpoint = getEndpointForPath(`/${sessionId}/events`, 'sessions');

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to list events: ${response.statusText}`);
                }

                return response.json();
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Agent Engine listEvents error:', error);
                throw error;
            }
        } else {
            // Local Backend: GET events for session
            const endpoint = getEndpointForPath(`/apps/${appName}/users/${userId}/sessions/${sessionId}/events`);

            try {
                const authHeaders = await getAuthHeaders();
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        ...authHeaders,
                    },
                });

                if (!response.ok) {
                    throw new Error(`Failed to list events: ${response.statusText}`);
                }

                const events = await response.json();

                console.log('✅ [ADK SESSION SERVICE] Local Backend listEvents success:', {
                    eventsCount: events.length,
                });

                return {
                    events,
                };
            } catch (error) {
                console.error('❌ [ADK SESSION SERVICE] Local Backend listEvents error:', error);
                throw error;
            }
        }
    }

    /**
     * Get a session with all its events (for historical context)
     * @param {string} userId - User identifier
     * @param {string} sessionId - Session identifier  
     * @returns {Promise<Object|null>} Session with events or null
     */
    static async getSessionWithEvents(userId, sessionId) {
        try {
            const session = await this.getSession(userId, sessionId);
            if (!session) {
                return null;
            }

            const eventsResult = await this.listEvents(userId, sessionId);
            return {
                ...session,
                events: eventsResult.events || []
            };
        } catch (error) {
            console.error('❌ [ADK SESSION SERVICE] getSessionWithEvents error:', error);
            return null;
        }
    }
}

// Convenience functions that use the AdkSessionService
export async function createSession(userId) {
    return await AdkSessionService.createSession(userId);
}

export async function getSessionWithEvents(userId, sessionId) {
    return await AdkSessionService.getSessionWithEvents(userId, sessionId);
}

export async function listUserSessions(userId) {
    return await AdkSessionService.listSessions(userId);
}

export default AdkSessionService;