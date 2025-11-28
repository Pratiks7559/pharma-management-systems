/**
 * Global Notification System
 * Provides toast notifications for success, error, warning, and info messages
 */

window.NotificationSystem = {
    container: null,
    
    init: function() {
        if (!this.container) {
            this.createContainer();
        }
    },
    
    createContainer: function() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    },
    
    show: function(message, type = 'info', duration = 5000) {
        this.init();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this.getIcon(type);
        const color = this.getColor(type);
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${icon} notification-icon"></i>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        notification.style.cssText = `
            background: ${color};
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease;
            pointer-events: auto;
            opacity: 0;
            transform: translateX(100%);
        `;
        
        this.container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }
        
        return notification;
    },
    
    remove: function(notification) {
        if (notification && notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
            }, 300);
        }
    },
    
    success: function(message, duration = 4000) {
        return this.show(message, 'success', duration);
    },
    
    error: function(message, duration = 6000) {
        return this.show(message, 'error', duration);
    },
    
    warning: function(message, duration = 5000) {
        return this.show(message, 'warning', duration);
    },
    
    info: function(message, duration = 4000) {
        return this.show(message, 'info', duration);
    },
    
    getIcon: function(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    },
    
    getColor: function(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#06b6d4'
        };
        return colors[type] || colors.info;
    }
};

// Global shorthand function
window.showNotification = function(message, type = 'info', duration = 5000) {
    return window.NotificationSystem.show(message, type, duration);
};

// Add CSS animations
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-icon {
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .notification-message {
        flex: 1;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 0.25rem;
        margin-left: auto;
        flex-shrink: 0;
        opacity: 0.8;
        transition: opacity 0.2s ease;
    }
    
    .notification-close:hover {
        opacity: 1;
        background: rgba(255, 255, 255, 0.2);
    }
    
    @media (max-width: 640px) {
        #notification-container {
            left: 10px;
            right: 10px;
            max-width: none;
        }
        
        .notification-message {
            font-size: 0.85rem;
        }
    }
`;
document.head.appendChild(notificationStyles);

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.NotificationSystem.init();
});