// Unified Date Utility for DDMMYYYY format handling
(function() {
    'use strict';

    // Validate DDMMYYYY format
    function validateDDMMYYYY(dateStr) {
        if (!dateStr || dateStr.length !== 8) return false;
        if (!/^\d{8}$/.test(dateStr)) return false;
        
        const day = parseInt(dateStr.substring(0, 2));
        const month = parseInt(dateStr.substring(2, 4));
        const year = parseInt(dateStr.substring(4, 8));
        
        if (month < 1 || month > 12) return false;
        if (day < 1 || day > 31) return false;
        if (year < 1900 || year > 2100) return false;
        
        // Check for valid day in month
        const daysInMonth = new Date(year, month, 0).getDate();
        return day <= daysInMonth;
    }

    // Convert DDMMYYYY to YYYY-MM-DD for backend
    function convertToBackendFormat(ddmmyyyy) {
        if (!ddmmyyyy || ddmmyyyy.length !== 8) return '';
        
        const day = ddmmyyyy.substring(0, 2);
        const month = ddmmyyyy.substring(2, 4);
        const year = ddmmyyyy.substring(4, 8);
        
        return `${year}-${month}-${day}`;
    }

    // Convert YYYY-MM-DD to DDMMYYYY for display
    function convertFromBackendFormat(backendDate) {
        if (!backendDate) return '';
        
        const date = new Date(backendDate);
        if (isNaN(date.getTime())) return backendDate;
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = String(date.getFullYear());
        
        return day + month + year;
    }

    // Format date input with validation
    function formatDateInput(input) {
        // Skip if already initialized or if it's a numeric field or expiry field
        if (input.hasAttribute('data-date-initialized') || 
            input.type === 'number' || 
            input.classList.contains('purchase-rate') ||
            input.classList.contains('purchase-rate-input') ||
            input.classList.contains('expiry') ||
            input.id.includes('purchase') ||
            input.id.includes('rate') ||
            input.id.includes('Rate') ||
            input.id.includes('Expiry') ||
            input.id.includes('expiry') ||
            input.placeholder && input.placeholder.includes('MM-YYYY')) return;
        input.setAttribute('data-date-initialized', 'true');
        
        // Set input attributes
        input.setAttribute('type', 'text');
        input.setAttribute('placeholder', 'DDMMYYYY');
        input.setAttribute('maxlength', '8');
        input.classList.add('date-input');
        
        // Convert existing value to DDMMYYYY if needed
        if (input.value && input.value.includes('-')) {
            const ddmmyyyy = convertFromBackendFormat(input.value);
            if (ddmmyyyy && ddmmyyyy.length === 8) {
                input.setAttribute('data-backend-value', input.value);
                input.value = ddmmyyyy;
            }
        }
        
        // Input event - format as user types
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) {
                value = value.substring(0, 8);
            }
            e.target.value = value;
            
            // Clear previous validation
            e.target.classList.remove('valid-date', 'invalid-date');
            e.target.style.borderColor = '';
            
            // Validate and provide feedback
            if (value.length === 8) {
                if (validateDDMMYYYY(value)) {
                    e.target.classList.add('valid-date');
                    e.target.style.borderColor = '#28a745';
                    e.target.title = `Valid date: ${value.substring(0,2)}/${value.substring(2,4)}/${value.substring(4,8)}`;
                    e.target.setAttribute('data-backend-value', convertToBackendFormat(value));
                } else {
                    e.target.classList.add('invalid-date');
                    e.target.style.borderColor = '#dc3545';
                    e.target.title = 'Invalid date';
                }
            } else if (value.length > 0) {
                e.target.style.borderColor = '#ffc107';
                e.target.title = 'Enter 8 digits (DDMMYYYY)';
            }
        });
        
        // Blur event - final validation
        input.addEventListener('blur', function(e) {
            const value = e.target.value;
            if (value && value.length > 0 && !validateDDMMYYYY(value)) {
                showDateError(e.target, 'Please enter a valid date in DDMMYYYY format');
                setTimeout(() => e.target.focus(), 100);
            }
        });
        
        // Keypress event - only allow numbers
        input.addEventListener('keypress', function(e) {
            if (!/\d/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    // Show date error message
    function showDateError(input, message) {
        // Remove existing error
        const existingError = input.parentElement.querySelector('.date-error-message');
        if (existingError) existingError.remove();
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'date-error-message';
        errorDiv.style.cssText = 'color: #dc3545; font-size: 12px; margin-top: 4px;';
        errorDiv.textContent = message;
        
        input.parentElement.appendChild(errorDiv);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 3000);
    }

    // Handle form submissions
    function handleFormSubmissions() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            const dateInputs = form.querySelectorAll('input[data-date-initialized="true"]');
            
            dateInputs.forEach(input => {
                const backendValue = input.getAttribute('data-backend-value');
                if (backendValue) {
                    // Create hidden input with backend format
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = input.name;
                    hiddenInput.value = backendValue;
                    
                    // Disable original input and add hidden input
                    input.disabled = true;
                    form.appendChild(hiddenInput);
                }
            });
        });
    }

    // Initialize date inputs
    function initializeDateInputs() {
        // Only target specific DDMMYYYY date inputs, not expiry fields
        const selectors = [
            'input.date-input-ddmmyyyy',
            'input[data-date-format="ddmmyyyy"]',
            'input[placeholder="DDMMYYYY"]'
        ];
        
        const dateInputs = document.querySelectorAll(selectors.join(', '));
        // Additional filter to exclude numeric inputs, purchase rate fields, and expiry fields
        const filteredInputs = Array.from(dateInputs).filter(input => {
            return input.type !== 'number' && 
                   !input.classList.contains('purchase-rate') && 
                   !input.classList.contains('purchase-rate-input') &&
                   !input.classList.contains('expiry') &&
                   !input.id.includes('purchase') &&
                   !input.id.includes('rate') &&
                   !input.id.includes('Rate') &&
                   !input.id.includes('expiry') &&
                   !input.id.includes('Expiry') &&
                   !input.name.includes('purchase_rate') &&
                   !input.name.includes('rate') &&
                   !input.name.includes('expiry') &&
                   !(input.placeholder && input.placeholder.includes('MM-YYYY'));
        });
        
        filteredInputs.forEach(formatDateInput);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initializeDateInputs();
            handleFormSubmissions();
        });
    } else {
        initializeDateInputs();
        handleFormSubmissions();
    }

    // Re-initialize for dynamic content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setTimeout(initializeDateInputs, 100);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Global API
    window.DateUtils = {
        validate: validateDDMMYYYY,
        toBackend: convertToBackendFormat,
        fromBackend: convertFromBackendFormat,
        initialize: initializeDateInputs
    };
})();