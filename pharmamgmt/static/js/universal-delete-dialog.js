// Universal Delete Confirmation Dialog System
function createDeleteDialog(itemType, itemId, itemName, deleteUrl) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    // Create modal content
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 12px;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        text-align: center;
    `;
    
    modal.innerHTML = `
        <div style="color: #ef4444; font-size: 3rem; margin-bottom: 1rem;">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3 style="margin: 0 0 1rem 0; color: #1f2937;">Delete ${itemType}</h3>
        <p style="margin: 0 0 1rem 0; color: #6b7280;">Are you sure you want to delete ${itemType.toLowerCase()} <strong>${itemName}</strong>? This action cannot be undone.</p>
        <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 8px 12px; margin-bottom: 1.5rem; font-size: 12px; color: #6c757d; text-align: center;">
            Press <kbd style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Enter</kbd> to confirm or <kbd style="background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Esc</kbd> to cancel
        </div>
        <div style="display: flex; gap: 1rem; justify-content: center;">
            <button id="cancelBtn" style="
                padding: 0.75rem 1.5rem;
                border: 2px solid #10b981;
                background: #10b981;
                color: white;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            ">Cancel</button>
            <button id="confirmBtn" style="
                padding: 0.75rem 1.5rem;
                border: 2px solid #ef4444;
                background: white;
                color: #ef4444;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            ">Delete</button>
        </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Get buttons
    const confirmBtn = modal.querySelector('#confirmBtn');
    const cancelBtn = modal.querySelector('#cancelBtn');
    
    // Focus on Delete button for quick Enter confirmation
    setTimeout(() => {
        confirmBtn.focus();
        // Add visual indication that Delete button is focused
        confirmBtn.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.3)';
    }, 100);
    
    // Add hover effects for Cancel button
    cancelBtn.addEventListener('mouseenter', () => {
        cancelBtn.style.background = '#059669';
        cancelBtn.style.transform = 'translateY(-2px)';
    });
    cancelBtn.addEventListener('mouseleave', () => {
        cancelBtn.style.background = '#10b981';
        cancelBtn.style.transform = 'translateY(0)';
    });
    
    // Add hover effects for Delete button
    confirmBtn.addEventListener('mouseenter', () => {
        confirmBtn.style.background = '#ef4444';
        confirmBtn.style.color = 'white';
        confirmBtn.style.transform = 'translateY(-2px)';
    });
    confirmBtn.addEventListener('mouseleave', () => {
        confirmBtn.style.background = 'white';
        confirmBtn.style.color = '#ef4444';
        confirmBtn.style.transform = 'translateY(0)';
    });
    
    // Handle Cancel action
    const performCancel = () => {
        document.removeEventListener('keydown', handleKeydown, true);
        document.body.removeChild(overlay);
    };
    
    cancelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        performCancel();
    });
    
    // Add focus event listeners for visual feedback
    confirmBtn.addEventListener('focus', () => {
        confirmBtn.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.3)';
    });
    
    confirmBtn.addEventListener('blur', () => {
        confirmBtn.style.boxShadow = '';
    });
    
    cancelBtn.addEventListener('focus', () => {
        cancelBtn.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.3)';
    });
    
    cancelBtn.addEventListener('blur', () => {
        cancelBtn.style.boxShadow = '';
    });
    
    // Handle Delete action
    const performDelete = () => {
        document.removeEventListener('keydown', handleKeydown, true);
        document.body.removeChild(overlay);
        
        // Show loading indicator
        const loadingOverlay = document.createElement('div');
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
        `;
        loadingOverlay.innerHTML = `
            <div style="text-align: center;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                <div>Deleting...</div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(loadingOverlay);
        
        // Use fetch API to submit delete request properly
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: 'csrfmiddlewaretoken=' + encodeURIComponent(getCSRFToken())
        })
        .then(response => {
            if (response.ok) {
                // Redirect to the appropriate list page or reload
                if (deleteUrl.includes('/products/')) {
                    window.location.href = '/products/';
                } else if (deleteUrl.includes('/customers/')) {
                    window.location.href = '/customers/';
                } else if (deleteUrl.includes('/suppliers/')) {
                    window.location.href = '/suppliers/';
                } else {
                    window.location.reload();
                }
            } else {
                throw new Error('Delete failed');
            }
        })
        .catch(error => {
            document.body.removeChild(loadingOverlay);
            alert('Error deleting item: ' + error.message);
        });
    };
    
    function getCSRFToken() {
        // Method 1: Look for existing CSRF input in forms
        const existingCsrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (existingCsrfInput) {
            return existingCsrfInput.value;
        }
        
        // Method 2: Look for CSRF meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Method 3: Look for CSRF cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        return '';
    }
    
    confirmBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        performDelete();
    });
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            document.removeEventListener('keydown', handleKeydown, true);
            document.body.removeChild(overlay);
        }
    });
    
    // Handle keyboard events
    const handleKeydown = (e) => {
        // Stop event from bubbling to prevent conflicts
        e.stopPropagation();
        
        if (e.key === 'Escape') {
            e.preventDefault();
            document.removeEventListener('keydown', handleKeydown, true);
            document.body.removeChild(overlay);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            // Always delete when Enter is pressed (Delete button is auto-focused)
            performDelete();
        } else if (e.key === 'Tab') {
            e.preventDefault();
            // Toggle focus between buttons
            if (document.activeElement === confirmBtn) {
                cancelBtn.focus();
                // Remove focus styling from confirm button
                confirmBtn.style.boxShadow = '';
                // Add focus styling to cancel button
                cancelBtn.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.3)';
            } else {
                confirmBtn.focus();
                // Remove focus styling from cancel button
                cancelBtn.style.boxShadow = '';
                // Add focus styling to confirm button
                confirmBtn.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.3)';
            }
        }
    };
    
    // Add event listener with capture to handle events before they bubble
    document.addEventListener('keydown', handleKeydown, true);
}

// Convenience functions for different item types
window.confirmDeleteCustomer = function(customerId, customerName) {
    createDeleteDialog('Customer', customerId, customerName, `/customers/${customerId}/delete/`);
};

window.confirmDeleteSupplier = function(supplierId, supplierName) {
    createDeleteDialog('Supplier', supplierId, supplierName, `/suppliers/${supplierId}/delete/`);
};

window.confirmDeleteProduct = function(productId, productName) {
    createDeleteDialog('Product', productId, productName, `/products/${productId}/delete/`);
};

window.confirmDeleteInvoice = function(invoiceId, invoiceNo) {
    createDeleteDialog('Invoice', invoiceId, `#${invoiceNo}`, `/invoices/${invoiceId}/delete/`);
};

window.confirmDeleteSalesInvoice = function(invoiceNo) {
    createDeleteDialog('Sales Invoice', invoiceNo, `#${invoiceNo}`, `/sales/${invoiceNo}/delete/`);
};

window.confirmDeleteUser = function(userId, username) {
    createDeleteDialog('User', userId, username, `/users/${userId}/delete/`);
};

// Generic delete function for any item
window.confirmDelete = function(itemType, itemId, itemName, deleteUrl) {
    createDeleteDialog(itemType, itemId, itemName, deleteUrl);
};

// Ctrl+D shortcut functionality
document.addEventListener('DOMContentLoaded', function() {
    // Find all delete buttons on the page
    function findDeleteButtons() {
        const selectors = [
            'a[href*="delete"]',
            'button[onclick*="delete"]',
            '.delete-btn',
            '.btn-delete',
            '.delete-button',
            '[data-action="delete"]',
            '.fa-trash',
            '.fa-trash-alt'
        ];
        
        let deleteButtons = [];
        selectors.forEach(selector => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(btn => {
                if (!deleteButtons.includes(btn)) {
                    deleteButtons.push(btn);
                }
            });
        });
        
        return deleteButtons.filter(btn => {
            const rect = btn.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0 && 
                   window.getComputedStyle(btn).visibility !== 'hidden' &&
                   window.getComputedStyle(btn).display !== 'none';
        });
    }
    
    // Extract item information from button context
    function extractItemInfo(button) {
        let itemName = '';
        let itemType = 'Item';
        
        // Try to get from data attributes
        itemName = button.dataset.itemName || button.dataset.name || '';
        itemType = button.dataset.itemType || itemType;
        
        // If no data attributes, try to find from context
        if (!itemName) {
            const row = button.closest('tr, .item, .card, .list-item');
            if (row) {
                const nameCell = row.querySelector('.name, .title, .product-name, .customer-name, .supplier-name');
                if (nameCell) {
                    itemName = nameCell.textContent.trim();
                }
            }
        }
        
        // Determine item type from URL if not set
        if (itemType === 'Item') {
            const url = button.href || window.location.pathname;
            if (url.includes('product')) itemType = 'Product';
            else if (url.includes('customer')) itemType = 'Customer';
            else if (url.includes('supplier')) itemType = 'Supplier';
            else if (url.includes('invoice')) itemType = 'Invoice';
            else if (url.includes('user')) itemType = 'User';
        }
        
        return { itemName: itemName || 'this item', itemType };
    }
    
    // Handle Ctrl+D shortcut
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            
            const deleteButtons = findDeleteButtons();
            
            if (deleteButtons.length === 0) {
                // Show "no delete action" message
                const messageOverlay = document.createElement('div');
                messageOverlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                
                const messageBox = document.createElement('div');
                messageBox.style.cssText = `
                    background: white;
                    padding: 2rem;
                    border-radius: 12px;
                    text-align: center;
                    max-width: 300px;
                `;
                
                messageBox.innerHTML = `
                    <div style="color: #3498db; font-size: 2rem; margin-bottom: 1rem;">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <p style="margin: 0; color: #2c3e50;">No delete action available on this page</p>
                    <small style="color: #7f8c8d; margin-top: 10px; display: block;">Press Esc to close</small>
                `;
                
                messageOverlay.appendChild(messageBox);
                document.body.appendChild(messageOverlay);
                
                const closeMessage = () => {
                    if (document.body.contains(messageOverlay)) {
                        document.body.removeChild(messageOverlay);
                    }
                };
                
                setTimeout(closeMessage, 2000);
                messageOverlay.addEventListener('click', closeMessage);
                document.addEventListener('keydown', function escHandler(e) {
                    if (e.key === 'Escape') {
                        closeMessage();
                        document.removeEventListener('keydown', escHandler);
                    }
                });
                
                return;
            }
            
            // Use the first visible delete button
            const targetButton = deleteButtons[0];
            const { itemName, itemType } = extractItemInfo(targetButton);
            
            // Extract delete URL
            let deleteUrl = targetButton.href;
            if (!deleteUrl && targetButton.onclick) {
                // Try to extract URL from onclick if it's a function call
                const onclickStr = targetButton.onclick.toString();
                const urlMatch = onclickStr.match(/['"]([^'"]*delete[^'"]*)['"]/);
                if (urlMatch) {
                    deleteUrl = urlMatch[1];
                }
            }
            
            if (deleteUrl) {
                createDeleteDialog(itemType, '', itemName, deleteUrl);
            } else {
                // Fallback: just click the button
                targetButton.click();
            }
        }
    });
});