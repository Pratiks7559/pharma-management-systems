// Global Date Formatter for DDMM format with auto-year completion
(function() {
    'use strict';

    // Auto-complete year when user enters DDMM format
    function autoCompleteYear(input) {
        let value = input.value.replace(/\D/g, ''); // Remove non-digits
        
        if (value.length === 4) {
            const currentYear = new Date().getFullYear();
            const day = value.substring(0, 2);
            const month = value.substring(2, 4);
            
            // Validate day and month
            if (parseInt(day) >= 1 && parseInt(day) <= 31 && 
                parseInt(month) >= 1 && parseInt(month) <= 12) {
                
                // Store original DDMM value
                input.setAttribute('data-ddmm-value', value);
                
                // Format as YYYY-MM-DD for backend compatibility
                const formattedDate = `${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                input.setAttribute('data-full-date', formattedDate);
                
                // Keep DDMM display for user
                input.value = value;
                input.classList.add('valid-date');
                input.classList.remove('invalid-date');
                
                // Show success feedback
                showDateFeedback(input, `Date: ${day}/${month}/${currentYear}`, 'success');
            } else {
                input.classList.add('invalid-date');
                input.classList.remove('valid-date');
                showDateFeedback(input, 'Invalid date format', 'error');
            }
        }
    }

    // Format date input as user types
    function formatDateInput(input) {
        let value = input.value.replace(/\D/g, '');
        
        // Limit to 4 digits (DDMM)
        if (value.length > 4) {
            value = value.substring(0, 4);
        }
        
        // Don't format if it's already in full date format
        if (input.value.includes('-') && input.value.length > 4) {
            return;
        }
        
        input.value = value;
        
        // Clear validation classes while typing
        input.classList.remove('valid-date', 'invalid-date');
        hideDateFeedback(input);
    }

    // Display date in DDMM format for user viewing
    function displayDateAsDDMM(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        
        return day + month;
    }

    // Convert DDMM to full date for backend
    function convertDDMMToFullDate(ddmmValue) {
        if (!ddmmValue || ddmmValue.length !== 4) return '';
        
        const currentYear = new Date().getFullYear();
        const day = ddmmValue.substring(0, 2);
        const month = ddmmValue.substring(2, 4);
        
        return `${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    // Show date feedback
    function showDateFeedback(input, message, type) {
        hideDateFeedback(input);
        
        const feedback = document.createElement('div');
        feedback.className = `date-feedback date-feedback-${type}`;
        feedback.textContent = message;
        feedback.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            font-size: 12px;
            padding: 2px 6px;
            border-radius: 3px;
            z-index: 1000;
            white-space: nowrap;
            ${type === 'success' ? 'background: #d4edda; color: #155724; border: 1px solid #c3e6cb;' : 'background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;'}
        `;
        
        const container = input.closest('.form-group') || input.parentElement;
        if (container) {
            container.style.position = 'relative';
            container.appendChild(feedback);
            
            setTimeout(() => hideDateFeedback(input), 3000);
        }
    }

    // Hide date feedback
    function hideDateFeedback(input) {
        const container = input.closest('.form-group') || input.parentElement;
        if (container) {
            const existing = container.querySelector('.date-feedback');
            if (existing) {
                existing.remove();
            }
        }
    }

    // Initialize date inputs
    function initializeDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"], input[name*="date"], input[id*="date"], input[class*="date-input"], input[placeholder*="DDMM"]');
        
        dateInputs.forEach(input => {
            // Skip if already initialized
            if (input.hasAttribute('data-ddmm-initialized')) return;
            
            // Mark as initialized
            input.setAttribute('data-ddmm-initialized', 'true');
            
            // Set attributes
            input.setAttribute('placeholder', 'DDMM');
            input.setAttribute('maxlength', '4');
            input.setAttribute('type', 'text'); // Force text input for DDMM format
            
            // Add event listeners
            input.addEventListener('input', function() {
                formatDateInput(this);
            });
            
            input.addEventListener('blur', function() {
                autoCompleteYear(this);
            });
            
            input.addEventListener('focus', function() {
                // Convert full date back to DDMM for editing
                const ddmmValue = this.getAttribute('data-ddmm-value');
                if (ddmmValue) {
                    this.value = ddmmValue;
                }
            });
            
            input.addEventListener('keypress', function(e) {
                // Only allow numbers
                if (!/\d/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                    e.preventDefault();
                }
            });
            
            // Convert existing values to DDMM format for display
            if (input.value && input.value.includes('-')) {
                const ddmmValue = displayDateAsDDMM(input.value);
                if (ddmmValue) {
                    input.setAttribute('data-full-date', input.value);
                    input.setAttribute('data-ddmm-value', ddmmValue);
                    input.value = ddmmValue;
                    input.classList.add('valid-date');
                }
            }
        });
    }

    // Handle form submissions to convert DDMM back to full date
    function handleFormSubmissions() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Skip if already initialized
            if (form.hasAttribute('data-ddmm-form-initialized')) return;
            form.setAttribute('data-ddmm-form-initialized', 'true');
            
            form.addEventListener('submit', function(e) {
                const dateInputs = this.querySelectorAll('input[data-ddmm-initialized="true"]');
                
                dateInputs.forEach(input => {
                    const fullDate = input.getAttribute('data-full-date');
                    if (fullDate) {
                        // Use the stored full date for submission
                        input.value = fullDate;
                    } else if (input.value && input.value.length === 4 && !input.value.includes('-')) {
                        // Convert DDMM to full date if not already converted
                        const convertedDate = convertDDMMToFullDate(input.value);
                        if (convertedDate) {
                            input.value = convertedDate;
                        }
                    }
                });
            });
        });
    }

    // Handle AJAX form submissions
    function handleAjaxSubmissions() {
        // Override jQuery's serialize methods if jQuery is available
        if (window.jQuery) {
            const originalSerialize = jQuery.fn.serialize;
            jQuery.fn.serialize = function() {
                // Convert DDMM dates before serialization
                this.find('input[data-ddmm-initialized="true"]').each(function() {
                    const fullDate = this.getAttribute('data-full-date');
                    if (fullDate) {
                        this.value = fullDate;
                    }
                });
                return originalSerialize.call(this);
            };
        }
    }

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeDateInputs();
        handleFormSubmissions();
        handleAjaxSubmissions();
    });

    // Re-initialize for dynamically added content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setTimeout(() => {
                    initializeDateInputs();
                    handleFormSubmissions();
                }, 100);
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Global functions for manual use
    window.DateFormatter = {
        displayAsDDMM: displayDateAsDDMM,
        convertToFullDate: convertDDMMToFullDate,
        initializeInputs: initializeDateInputs,
        autoCompleteYear: autoCompleteYear
    };
})();