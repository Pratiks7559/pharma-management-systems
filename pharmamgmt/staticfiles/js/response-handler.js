/**
 * Response Handler Utility
 * Provides safe JSON parsing for fetch responses
 */

window.ResponseHandler = {
    /**
     * Safely parse JSON response with proper error handling
     * @param {Response} response - Fetch API response object
     * @returns {Promise} - Promise that resolves to parsed JSON or rejects with error
     */
    parseJSON: function(response) {
        return new Promise((resolve, reject) => {
            // Check if response is ok
            if (!response.ok) {
                reject(new Error(`HTTP ${response.status}: ${response.statusText}`));
                return;
            }
            
            // Check if response has content
            const contentLength = response.headers.get('content-length');
            if (contentLength === '0') {
                reject(new Error('Empty response'));
                return;
            }
            
            // Check content type
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                reject(new Error('Response is not JSON'));
                return;
            }
            
            // Try to parse JSON
            response.json()
                .then(data => resolve(data))
                .catch(error => reject(new Error('Invalid JSON: ' + error.message)));
        });
    },
    
    /**
     * Safe fetch with JSON parsing
     * @param {string} url - URL to fetch
     * @param {object} options - Fetch options
     * @returns {Promise} - Promise that resolves to parsed JSON
     */
    fetchJSON: function(url, options = {}) {
        return fetch(url, options)
            .then(response => this.parseJSON(response));
    },
    
    /**
     * Handle common fetch errors
     * @param {Error} error - Error object
     * @returns {string} - User-friendly error message
     */
    getErrorMessage: function(error) {
        if (error.message.includes('Failed to fetch')) {
            return 'Network error. Please check your connection.';
        } else if (error.message.includes('HTTP 404')) {
            return 'Resource not found.';
        } else if (error.message.includes('HTTP 500')) {
            return 'Server error. Please try again later.';
        } else if (error.message.includes('Response is not JSON')) {
            return 'Invalid server response.';
        } else if (error.message.includes('Empty response')) {
            return 'No data received from server.';
        } else {
            return error.message || 'An unexpected error occurred.';
        }
    }
};

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Show user-friendly error message
    if (window.showNotification) {
        window.showNotification(
            window.ResponseHandler.getErrorMessage(event.reason), 
            'error'
        );
    }
});