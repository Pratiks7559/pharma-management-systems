// Flexible Date Input Handler
(function() {
    'use strict';

    function formatDateInput(dateStr) {
        if (!dateStr) return '';
        
        // Remove all non-digits
        let clean = dateStr.replace(/[^0-9]/g, '');
        
        // Handle ddmmyyyy format (8 digits)
        if (clean.length === 8) {
            const day = clean.substring(0, 2);
            const month = clean.substring(2, 4);
            const year = clean.substring(4, 8);
            return `${year}-${month}-${day}`;
        }
        
        // Return original if not 8 digits
        return dateStr;
    }

    function displayDateForUser(dateStr) {
        if (!dateStr) return '';
        
        // If it's yyyy-mm-dd format, convert to dd-mm-yyyy for display
        if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const parts = dateStr.split('-');
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        
        return dateStr;
    }

    function initializeDateInputs() {
        const dateInputs = document.querySelectorAll('.date-input, input[name*="date"]:not([type="number"]):not([class*="purchase-rate"]), input[id*="date"]:not([type="number"]):not([class*="purchase-rate"])');
        
        // Filter out purchase rate and numeric fields
        const filteredInputs = Array.from(dateInputs).filter(input => {
            return input.type !== 'number' && 
                   !input.classList.contains('purchase-rate') && 
                   !input.classList.contains('purchase-rate-input') &&
                   !input.id.includes('purchase') &&
                   !input.id.includes('rate') &&
                   !input.id.includes('Rate') &&
                   !input.name.includes('purchase_rate');
        });
        
        filteredInputs.forEach(input => {
            if (input.hasAttribute('data-flexible-date-initialized') || 
                input.type === 'number' || 
                input.classList.contains('purchase-rate')) return;
            input.setAttribute('data-flexible-date-initialized', 'true');
            
            // Convert existing value for display
            if (input.value && input.value.match(/^\d{4}-\d{2}-\d{2}$/)) {
                input.value = displayDateForUser(input.value);
            }
            
            input.addEventListener('blur', function() {
                if (this.value) {
                    // Store formatted value for form submission
                    const formatted = formatDateInput(this.value);
                    this.setAttribute('data-formatted-date', formatted);
                }
            });
        });
    }

    function handleFormSubmission() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            if (form.hasAttribute('data-flexible-date-form-initialized')) return;
            form.setAttribute('data-flexible-date-form-initialized', 'true');
            
            form.addEventListener('submit', function(e) {
                const dateInputs = this.querySelectorAll('input[data-flexible-date-initialized="true"]');
                
                dateInputs.forEach(input => {
                    if (input.value) {
                        const formatted = formatDateInput(input.value);
                        if (formatted !== input.value) {
                            input.value = formatted;
                        }
                    }
                });
            });
        });
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeDateInputs();
        handleFormSubmission();
    });

    // Re-initialize for dynamic content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                setTimeout(() => {
                    initializeDateInputs();
                    handleFormSubmission();
                    replaceErrorMessages();
                }, 100);
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Run error message replacement periodically
    setInterval(replaceErrorMessages, 1000);

    // Global function for AJAX usage
    window.formatDateInput = formatDateInput;
})();