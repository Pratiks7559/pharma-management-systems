// Universal Keyboard Navigation for All Lists and Tables
document.addEventListener('DOMContentLoaded', function() {
    let currentRowIndex = -1;
    let tableRows = [];
    let isNavigationActive = false;

    // Initialize navigation
    function initKeyboardNavigation() {
        // Find all table rows or list items
        const tables = document.querySelectorAll('table tbody tr, .list-item, .data-row');
        tableRows = Array.from(tables).filter(row => {
            // Exclude empty rows and header rows
            return !row.classList.contains('empty-message') && 
                   !row.classList.contains('header-row') &&
                   row.style.display !== 'none';
        });

        if (tableRows.length > 0) {
            setupKeyboardListeners();
        }
    }

    // Setup keyboard event listeners
    function setupKeyboardListeners() {
        document.addEventListener('keydown', function(e) {
            // Don't interfere if user is typing in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                return;
            }

            switch(e.key) {
                case 'ArrowDown':
                case 'j': // Vim-style navigation
                    e.preventDefault();
                    navigateDown();
                    break;
                
                case 'ArrowUp':
                case 'k': // Vim-style navigation
                    e.preventDefault();
                    navigateUp();
                    break;
                
                case 'Enter':
                case ' ': // Spacebar
                    e.preventDefault();
                    activateCurrentRow();
                    break;
                
                case 'Home':
                    e.preventDefault();
                    navigateToFirst();
                    break;
                
                case 'End':
                    e.preventDefault();
                    navigateToLast();
                    break;
                
                case 'PageDown':
                    e.preventDefault();
                    navigatePageDown();
                    break;
                
                case 'PageUp':
                    e.preventDefault();
                    navigatePageUp();
                    break;

                case 'Escape':
                    e.preventDefault();
                    clearSelection();
                    break;

                // Quick actions
                case 'n':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        triggerAddAction();
                    }
                    break;

                case 'e':
                    if (e.ctrlKey && currentRowIndex >= 0) {
                        e.preventDefault();
                        triggerEditAction();
                    }
                    break;

                case 'v':
                    if (e.ctrlKey && currentRowIndex >= 0) {
                        e.preventDefault();
                        triggerViewAction();
                    }
                    break;
            }
        });
    }

    // Navigation functions
    function navigateDown() {
        if (tableRows.length === 0) return;
        
        currentRowIndex = Math.min(currentRowIndex + 1, tableRows.length - 1);
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function navigateUp() {
        if (tableRows.length === 0) return;
        
        if (currentRowIndex <= 0) {
            currentRowIndex = 0;
        } else {
            currentRowIndex--;
        }
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function navigateToFirst() {
        if (tableRows.length === 0) return;
        
        currentRowIndex = 0;
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function navigateToLast() {
        if (tableRows.length === 0) return;
        
        currentRowIndex = tableRows.length - 1;
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function navigatePageDown() {
        if (tableRows.length === 0) return;
        
        const pageSize = Math.floor(window.innerHeight / 50); // Approximate rows per page
        currentRowIndex = Math.min(currentRowIndex + pageSize, tableRows.length - 1);
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function navigatePageUp() {
        if (tableRows.length === 0) return;
        
        const pageSize = Math.floor(window.innerHeight / 50);
        currentRowIndex = Math.max(currentRowIndex - pageSize, 0);
        highlightCurrentRow();
        scrollToCurrentRow();
        isNavigationActive = true;
    }

    function clearSelection() {
        // Remove highlight from all rows
        tableRows.forEach(row => {
            row.classList.remove('keyboard-selected');
            row.style.backgroundColor = '';
            row.style.outline = '';
        });
        currentRowIndex = -1;
        isNavigationActive = false;
    }

    // Highlight current row
    function highlightCurrentRow() {
        // Clear previous highlights
        tableRows.forEach(row => {
            row.classList.remove('keyboard-selected');
            row.style.backgroundColor = '';
            row.style.outline = '';
        });

        // Highlight current row
        if (currentRowIndex >= 0 && currentRowIndex < tableRows.length) {
            const currentRow = tableRows[currentRowIndex];
            currentRow.classList.add('keyboard-selected');
            currentRow.style.backgroundColor = '#e3f2fd';
            currentRow.style.outline = '2px solid #2196f3';
            currentRow.style.outlineOffset = '-1px';
        }
    }

    // Scroll to current row
    function scrollToCurrentRow() {
        if (currentRowIndex >= 0 && currentRowIndex < tableRows.length) {
            const currentRow = tableRows[currentRowIndex];
            currentRow.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }

    // Activate current row (click first link or button)
    function activateCurrentRow() {
        if (currentRowIndex >= 0 && currentRowIndex < tableRows.length) {
            const currentRow = tableRows[currentRowIndex];
            
            // Try to find and click the first actionable element
            const link = currentRow.querySelector('a[href]');
            const button = currentRow.querySelector('button');
            
            if (link) {
                link.click();
            } else if (button) {
                button.click();
            }
        }
    }

    // Quick action functions
    function triggerAddAction() {
        // Look for add/new buttons
        const addButtons = document.querySelectorAll('a[href*="add"], a[href*="new"], .add-btn, .new-btn');
        if (addButtons.length > 0) {
            addButtons[0].click();
        }
    }

    function triggerEditAction() {
        if (currentRowIndex >= 0 && currentRowIndex < tableRows.length) {
            const currentRow = tableRows[currentRowIndex];
            const editLink = currentRow.querySelector('a[href*="edit"], a[href*="update"], .btn-edit, .edit-btn');
            if (editLink) {
                editLink.click();
            }
        }
    }

    function triggerViewAction() {
        if (currentRowIndex >= 0 && currentRowIndex < tableRows.length) {
            const currentRow = tableRows[currentRowIndex];
            const viewLink = currentRow.querySelector('a[href*="detail"], a[href*="view"], .btn-view, .view-btn');
            if (viewLink) {
                viewLink.click();
            }
        }
    }

    // Handle pagination navigation
    function setupPaginationNavigation() {
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if (e.key === 'ArrowLeft' && e.ctrlKey) {
                e.preventDefault();
                const prevLink = document.querySelector('a .fa-angle-left');
                if (prevLink) {
                    prevLink.closest('a').click();
                }
            }

            if (e.key === 'ArrowRight' && e.ctrlKey) {
                e.preventDefault();
                const nextLink = document.querySelector('a .fa-angle-right');
                if (nextLink) {
                    nextLink.closest('a').click();
                }
            }
        });
    }

    // Show keyboard shortcuts help
    function showKeyboardHelp() {
        if (document.getElementById('keyboard-help-modal')) return;

        const helpModal = document.createElement('div');
        helpModal.id = 'keyboard-help-modal';
        helpModal.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; display: flex; align-items: center; justify-content: center;">
                <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 500px; width: 90%;">
                    <h3 style="margin-top: 0;">Keyboard Shortcuts</h3>
                    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 0.5rem; font-size: 0.9rem;">
                        <strong>↑/↓ or j/k</strong><span>Navigate rows</span>
                        <strong>Enter/Space</strong><span>Activate row</span>
                        <strong>Home/End</strong><span>First/Last row</span>
                        <strong>Page Up/Down</strong><span>Page navigation</span>
                        <strong>Ctrl + ←/→</strong><span>Previous/Next page</span>
                        <strong>Ctrl + N</strong><span>Add new item</span>
                        <strong>Ctrl + E</strong><span>Edit selected</span>
                        <strong>Ctrl + V</strong><span>View selected</span>
                        <strong>Escape</strong><span>Clear selection</span>
                        <strong>?</strong><span>Show this help</span>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(helpModal);
    }

    // Show help on ? key
    document.addEventListener('keydown', function(e) {
        if (e.key === '?' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            showKeyboardHelp();
        }
    });

    // Universal Enter Key Support for All Focusable Elements
    function setupUniversalEnterSupport() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                const activeElement = document.activeElement;
                
                // Skip if already in input fields or textareas
                if (activeElement.matches('input[type="text"], input[type="email"], input[type="password"], input[type="number"], input[type="search"], textarea, select')) {
                    return;
                }
                
                // Skip delete buttons and confirmation dialogs completely
                if (activeElement.matches('.btn-delete, .delete-btn, .supplier-list-btn-delete, [onclick*="delete"], [onclick*="Delete"], [onclick*="confirm"]')) {
                    return;
                }
                
                // Skip if element has onclick with confirm functions
                if (activeElement.hasAttribute('onclick') && (activeElement.getAttribute('onclick').includes('confirm') || activeElement.getAttribute('onclick').includes('Delete'))) {
                    return;
                }
                
                // Handle different types of focusable elements
                if (activeElement.matches('button, input[type="button"], input[type="submit"], input[type="reset"]')) {
                    // For buttons, trigger click
                    e.preventDefault();
                    activeElement.click();
                } else if (activeElement.matches('a[href]')) {
                    // For links, trigger click (will navigate)
                    e.preventDefault();
                    activeElement.click();
                } else if (activeElement.matches('input[type="checkbox"], input[type="radio"]')) {
                    // For checkboxes and radio buttons, toggle/select
                    e.preventDefault();
                    activeElement.click();
                } else if (activeElement.matches('[onclick], [data-action], .clickable')) {
                    // For elements with click handlers (excluding delete functions)
                    e.preventDefault();
                    activeElement.click();
                } else if (activeElement.matches('[tabindex], [role="button"], [role="link"]')) {
                    // For custom interactive elements
                    e.preventDefault();
                    activeElement.click();
                }
            }
        });
    }

    // Enhanced Tab Navigation with Visual Feedback
    function setupEnhancedTabNavigation() {
        let lastFocusedElement = null;
        
        document.addEventListener('focusin', function(e) {
            const element = e.target;
            
            // Add visual focus indicator for better accessibility
            if (element.matches('button, a, input, select, textarea, [tabindex]')) {
                // Remove previous focus styling
                if (lastFocusedElement) {
                    lastFocusedElement.style.boxShadow = lastFocusedElement.dataset.originalBoxShadow || '';
                    delete lastFocusedElement.dataset.originalBoxShadow;
                }
                
                // Store original box-shadow and add focus styling
                element.dataset.originalBoxShadow = element.style.boxShadow || '';
                element.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.5)';
                
                lastFocusedElement = element;
            }
        });
        
        document.addEventListener('focusout', function(e) {
            const element = e.target;
            
            // Restore original styling when focus is lost
            setTimeout(() => {
                if (document.activeElement !== element) {
                    element.style.boxShadow = element.dataset.originalBoxShadow || '';
                    delete element.dataset.originalBoxShadow;
                }
            }, 100);
        });
    }

    // Make all buttons and links keyboard accessible
    function makeElementsKeyboardAccessible() {
        // Find all interactive elements that might not be properly accessible
        const interactiveElements = document.querySelectorAll(
            'button:not([tabindex]), ' +
            'a[href]:not([tabindex]), ' +
            '[onclick]:not([tabindex]):not(input):not(button):not(a), ' +
            '.btn:not([tabindex]), ' +
            '.clickable:not([tabindex]), ' +
            '[data-action]:not([tabindex])'
        );
        
        interactiveElements.forEach(element => {
            // Ensure element is focusable
            if (!element.hasAttribute('tabindex')) {
                element.setAttribute('tabindex', '0');
            }
            
            // Add role if not present
            if (!element.hasAttribute('role') && !element.matches('button, a, input')) {
                element.setAttribute('role', 'button');
            }
            
            // Add keyboard event listener if not already present
            if (!element.dataset.keyboardEnabled) {
                element.dataset.keyboardEnabled = 'true';
                
                element.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.click();
                    }
                });
            }
        });
    }

    // Initialize everything
    initKeyboardNavigation();
    setupPaginationNavigation();
    setupUniversalEnterSupport();
    setupEnhancedTabNavigation();
    makeElementsKeyboardAccessible();

    // Re-initialize when content changes (for AJAX loaded content)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                setTimeout(() => {
                    initKeyboardNavigation();
                    makeElementsKeyboardAccessible();
                }, 100);
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});