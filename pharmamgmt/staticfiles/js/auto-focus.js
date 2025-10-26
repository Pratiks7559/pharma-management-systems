// Global Auto-Focus Script - AGGRESSIVE VERSION
// Automatically focuses on the first input field on any page

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Auto-focus script loaded');
    
    // Multiple attempts with increasing delays
    setTimeout(autoFocusFirstInput, 50);
    setTimeout(autoFocusFirstInput, 100);
    setTimeout(autoFocusFirstInput, 300);
    setTimeout(autoFocusFirstInput, 500);
    setTimeout(autoFocusFirstInput, 1000);
    setTimeout(autoFocusFirstInput, 2000);
    
    // Setup modal autofocus handlers
    setupModalAutofocus();
});

// Also try when window loads
window.addEventListener('load', function() {
    setTimeout(autoFocusFirstInput, 100);
    setTimeout(autoFocusFirstInput, 500);
});

function autoFocusFirstInput() {
    console.log('🔍 Searching for first input...');
    
    // Find ALL possible input elements
    const allInputs = document.querySelectorAll('input, select, textarea');
    console.log('📝 Found', allInputs.length, 'total inputs');
    
    // Filter for focusable ones
    const focusableInputs = Array.from(allInputs).filter(input => {
        return !input.disabled && 
               !input.readOnly && 
               input.type !== 'hidden' && 
               input.style.display !== 'none' &&
               input.offsetParent !== null; // Check if visible
    });
    
    console.log('✅ Found', focusableInputs.length, 'focusable inputs');
    
    if (focusableInputs.length > 0) {
        const firstInput = focusableInputs[0];
        
        try {
            // Force focus with multiple methods
            firstInput.removeAttribute('readonly');
            firstInput.removeAttribute('disabled');
            
            // Add temporary visual indicator
            firstInput.style.outline = '3px solid #007bff';
            firstInput.style.outlineOffset = '2px';
            firstInput.style.backgroundColor = '#e3f2fd';
            
            // Focus without scrolling to prevent keyboard navigation interference
            firstInput.focus({ preventScroll: true });
            
            // Only scroll if element is not visible in viewport
            const rect = firstInput.getBoundingClientRect();
            const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
            
            if (!isVisible) {
                firstInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Remove visual indicator after 2 seconds
            setTimeout(() => {
                firstInput.style.outline = '';
                firstInput.style.outlineOffset = '';
                firstInput.style.backgroundColor = '';
            }, 2000);
            
            console.log('✅ FOCUSED on:', {
                name: firstInput.name,
                id: firstInput.id,
                type: firstInput.type,
                tagName: firstInput.tagName,
                className: firstInput.className
            });
            
            return true;
        } catch (error) {
            console.error('❌ Focus error:', error);
            return false;
        }
    } else {
        console.log('⚠️ No focusable input found on this page');
        return false;
    }
}

// Export for manual use
window.autoFocusFirstInput = autoFocusFirstInput;
window.focusFirstModalInput = focusFirstModalInput;

// Setup modal autofocus for edit dialog boxes
function setupModalAutofocus() {
    console.log('🎯 Setting up modal autofocus handlers');
    
    // Sales Invoice Detail - Edit Modal
    document.addEventListener('click', function(e) {
        if (e.target.matches('.edit-invoice-action-btn, .edit-invoice-header-btn') || 
            e.target.closest('.edit-invoice-action-btn, .edit-invoice-header-btn')) {
            setTimeout(() => {
                focusFirstModalInput('#editSalesInvoiceModal');
            }, 300);
        }
    });
    
    // Purchase Invoice Detail - Edit Modal
    document.addEventListener('click', function(e) {
        if (e.target.matches('.invoice-edit-btn') || 
            e.target.closest('.invoice-edit-btn')) {
            setTimeout(() => {
                focusFirstModalInput('#editInvoiceModal');
            }, 300);
        }
    });
    
    // Sales Return Detail - Edit Modal
    document.addEventListener('click', function(e) {
        if (e.target.matches('button[onclick*="openEditSalesReturnModal"]') || 
            e.target.closest('button[onclick*="openEditSalesReturnModal"]')) {
            setTimeout(() => {
                focusFirstModalInput('#editSalesReturnModal');
            }, 300);
        }
    });
    
    // Purchase Return Detail - Edit Modal
    document.addEventListener('click', function(e) {
        if (e.target.matches('button[onclick*="openEditPurchaseReturnModal"]') || 
            e.target.closest('button[onclick*="openEditPurchaseReturnModal"]')) {
            setTimeout(() => {
                focusFirstModalInput('#editPurchaseReturnModal');
            }, 300);
        }
    });
    
    // Generic modal opener detection
    document.addEventListener('click', function(e) {
        const button = e.target.closest('button');
        if (button && button.textContent.toLowerCase().includes('edit')) {
            setTimeout(() => {
                // Try to find any visible modal and focus first input
                const visibleModals = document.querySelectorAll('.modal[style*="block"], .modal-overlay[style*="flex"], .modal-overlay[style*="block"]');
                visibleModals.forEach(modal => {
                    if (modal.offsetParent !== null) { // Check if visible
                        focusFirstModalInput('#' + modal.id);
                    }
                });
            }, 300);
        }
    });
}

// Focus first input in a specific modal
function focusFirstModalInput(modalSelector) {
    const modal = document.querySelector(modalSelector);
    if (!modal) {
        console.log(`⚠️ Modal ${modalSelector} not found`);
        return;
    }
    
    // Check if modal is visible
    const isVisible = modal.style.display === 'block' || 
                     modal.style.display === 'flex' || 
                     modal.offsetParent !== null;
    
    if (!isVisible) {
        console.log(`⚠️ Modal ${modalSelector} not visible`);
        return;
    }
    
    console.log(`🎯 Focusing first input in modal: ${modalSelector}`);
    
    // Find all focusable inputs in the modal
    const focusableInputs = modal.querySelectorAll('input:not([type="hidden"]):not([readonly]):not([disabled]), select:not([disabled]), textarea:not([disabled])');
    
    if (focusableInputs.length > 0) {
        const firstInput = focusableInputs[0];
        
        // Add visual indicator
        firstInput.style.outline = '3px solid #007bff';
        firstInput.style.outlineOffset = '2px';
        firstInput.style.backgroundColor = '#e3f2fd';
        
        // Focus and select
        firstInput.focus();
        if (firstInput.type === 'text' || firstInput.type === 'date' || firstInput.type === 'number') {
            firstInput.select();
        }
        
        // Remove visual indicator after 2 seconds
        setTimeout(() => {
            firstInput.style.outline = '';
            firstInput.style.outlineOffset = '';
            firstInput.style.backgroundColor = '';
        }, 2000);
        
        console.log(`✅ Focused on modal input:`, {
            modal: modalSelector,
            input: firstInput.name || firstInput.id || firstInput.className,
            type: firstInput.type,
            tagName: firstInput.tagName
        });
        
        return true;
    } else {
        console.log(`⚠️ No focusable inputs found in modal: ${modalSelector}`);
        return false;
    }
}

// Enhanced tab navigation for modal inputs
function setupModalTabNavigation() {
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            const activeModal = document.querySelector('.modal[style*="block"], .modal-overlay[style*="flex"], .modal-overlay[style*="block"]');
            if (activeModal) {
                const focusableElements = activeModal.querySelectorAll(
                    'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled])'
                );
                
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    // Shift + Tab (backward)
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    // Tab (forward)
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        }
    });
}

// Initialize modal tab navigation
setupModalTabNavigation();

// Add manual trigger button for testing
