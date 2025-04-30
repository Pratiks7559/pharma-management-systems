/**
 * Session Timer
 * Shows a countdown timer for session expiration and provides warnings
 */
 
// Configuration
const SESSION_TIMEOUT = 30 * 60; // 30 minutes in seconds
const WARNING_THRESHOLD = 5 * 60; // Show warning 5 minutes before expiry
const WARNING_INTERVAL = 60; // Show warning every 60 seconds after threshold
const REDIRECT_URL = '/login/'; // Redirect here after session expires

// Global variables
let sessionTimer;
let countdownInterval;
let warningShown = false;
let lastWarningTime = 0;

// Initialize the session timer
function initSessionTimer() {
    // Reset session timer when the page loads
    resetSessionTimer();
    
    // Add event listeners for user activity
    ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
        document.addEventListener(event, resetSessionTimer);
    });
    
    // Display timer in navbar if element exists
    updateTimerDisplay();
}

// Reset the session timer
function resetSessionTimer() {
    // Clear existing timer and intervals
    clearTimeout(sessionTimer);
    clearInterval(countdownInterval);
    
    // Reset warning flag
    warningShown = false;
    
    // Start a new timer
    sessionTimer = setTimeout(endSession, SESSION_TIMEOUT * 1000);
    
    // Start countdown display
    startCountdown();
}

// Start the countdown display
function startCountdown() {
    const startTime = Date.now();
    const endTime = startTime + (SESSION_TIMEOUT * 1000);
    
    countdownInterval = setInterval(() => {
        const currentTime = Date.now();
        const timeLeft = Math.max(0, endTime - currentTime);
        const secondsLeft = Math.floor(timeLeft / 1000);
        
        // Update timer display
        updateTimerDisplay(secondsLeft);
        
        // Show warning if approaching timeout
        if (secondsLeft <= WARNING_THRESHOLD && secondsLeft > 0) {
            const timeSinceLastWarning = (currentTime - lastWarningTime) / 1000;
            
            // Show initial warning or repeat warnings at intervals
            if (!warningShown || timeSinceLastWarning >= WARNING_INTERVAL) {
                showSessionWarning(secondsLeft);
                warningShown = true;
                lastWarningTime = currentTime;
            }
        }
        
        // End session when time runs out
        if (secondsLeft <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
}

// Update the timer display in the navbar
function updateTimerDisplay(secondsLeft = SESSION_TIMEOUT) {
    const timerElement = document.getElementById('session-timer');
    if (timerElement) {
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Add warning class when time is getting low
        if (secondsLeft <= WARNING_THRESHOLD) {
            timerElement.classList.add('text-danger');
            timerElement.classList.add('fw-bold');
        } else {
            timerElement.classList.remove('text-danger');
            timerElement.classList.remove('fw-bold');
        }
    }
}

// Show session warning modal
function showSessionWarning(secondsLeft) {
    const minutes = Math.floor(secondsLeft / 60);
    const seconds = secondsLeft % 60;
    const timeString = `${minutes}m ${seconds}s`;
    
    // Create or use existing modal
    let warningModal = document.getElementById('session-warning-modal');
    
    if (!warningModal) {
        // Create modal if it doesn't exist
        const modalHtml = `
            <div class="modal fade" id="session-warning-modal" tabindex="-1" aria-labelledby="sessionWarningModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-warning">
                            <h5 class="modal-title" id="sessionWarningModalLabel">
                                <i class="fas fa-exclamation-triangle me-2"></i>Session Expiring
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Your session will expire in <span id="warning-time-left">${timeString}</span>.</p>
                            <p>Click "Continue Session" to stay logged in, or your session will end automatically.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="resetSessionTimer()">
                                Continue Session
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="endSession()">
                                Logout Now
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to document
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer.firstChild);
        
        // Get the modal reference
        warningModal = document.getElementById('session-warning-modal');
    } else {
        // Update time in existing modal
        const timeLeftElement = document.getElementById('warning-time-left');
        if (timeLeftElement) {
            timeLeftElement.textContent = timeString;
        }
    }
    
    // Show the modal
    const bsModal = new bootstrap.Modal(warningModal);
    bsModal.show();
}

// End the session
function endSession() {
    // Clear timers
    clearTimeout(sessionTimer);
    clearInterval(countdownInterval);
    
    // Redirect to login page
    window.location.href = REDIRECT_URL;
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initSessionTimer);