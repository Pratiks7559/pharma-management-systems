/**
 * Sales Challan Invoice List JavaScript
 * Handles payment modal, form submissions, and keyboard shortcuts
 */

// Sales Challan Payment Modal Functions
function showSalesChallanPaymentDialog(invoiceId, invoiceNo, balance) {
    const modal = document.getElementById('salesChallanPaymentModal');
    const invoiceNoElement = document.getElementById('salesChallanPaymentInvoiceNo');
    const balanceElement = document.getElementById('salesChallanPaymentBalance');
    const amountInput = document.getElementById('salesChallanPaymentAmount');
    const dateInput = document.getElementById('salesChallanPaymentDate');
    const form = document.getElementById('salesChallanPaymentForm');
    
    if (!modal || !invoiceNoElement || !balanceElement || !amountInput || !form) {
        console.error('Required modal elements not found');
        return;
    }
    
    // Set invoice details
    invoiceNoElement.textContent = invoiceNo;
    balanceElement.textContent = parseFloat(balance).toFixed(2);
    amountInput.value = parseFloat(balance).toFixed(2);
    amountInput.max = parseFloat(balance).toFixed(2);
    
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    
    // Store invoice ID for form submission
    form.setAttribute('data-invoice-id', invoiceId);
    
    // Show modal and focus on amount input
    modal.style.display = 'flex';
    setTimeout(() => amountInput.focus(), 100);
}

function hideSalesChallanPaymentModal() {
    const modal = document.getElementById('salesChallanPaymentModal');
    const form = document.getElementById('salesChallanPaymentForm');
    
    if (modal) {
        modal.style.display = 'none';
    }
    
    if (form) {
        form.reset();
        form.removeAttribute('data-invoice-id');
    }
}

// Initialize payment form handler
function initializePaymentForm() {
    const form = document.getElementById('salesChallanPaymentForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const invoiceId = this.getAttribute('data-invoice-id');
        if (!invoiceId) {
            alert('Invoice ID not found');
            return;
        }
        
        const formData = new FormData(this);
        const submitBtn = document.querySelector('#salesChallanPaymentForm .payment-btn-save');
        
        // Validate payment amount
        const amount = parseFloat(formData.get('payment_amount'));
        const maxAmount = parseFloat(document.getElementById('salesChallanPaymentAmount').max);
        
        if (isNaN(amount) || amount <= 0) {
            alert('Please enter a valid payment amount');
            return;
        }
        
        if (amount > maxAmount + 0.01) {
            alert(`Payment amount cannot exceed balance due of ₹${maxAmount.toFixed(2)}`);
            return;
        }
        
        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Adding Payment...';
        }
        
        // Submit payment
        fetch(`/sales/challan-invoices/${invoiceId}/add-payment/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Payment added successfully!');
                hideSalesChallanPaymentModal();
                window.location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            console.error('Payment error:', error);
            alert('Error adding payment. Please try again.');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Add Payment';
            }
        });
    });
}

// Initialize modal click outside handler
function initializeModalHandlers() {
    const modal = document.getElementById('salesChallanPaymentModal');
    if (!modal) return;
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            hideSalesChallanPaymentModal();
        }
    });
    
    // Close button handler
    const closeBtn = modal.querySelector('.payment-modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideSalesChallanPaymentModal);
    }
}

// Initialize keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        const modal = document.getElementById('salesChallanPaymentModal');
        
        // Modal-specific shortcuts
        if (modal && modal.style.display === 'flex') {
            if (e.key === 'Escape') {
                e.preventDefault();
                hideSalesChallanPaymentModal();
            } else if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                const form = document.getElementById('salesChallanPaymentForm');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
            return;
        }
        
        // Global shortcuts for the page
        if (e.ctrlKey) {
            switch(e.key.toLowerCase()) {
                case 'f':
                    e.preventDefault();
                    const searchInput = document.querySelector('.sales-challan-invoice-list-search-input');
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                    break;
                    
                case 'r':
                    e.preventDefault();
                    window.location.reload();
                    break;
            }
        }
    });
}

// Initialize search functionality
function initializeSearchFeatures() {
    const searchInput = document.querySelector('.sales-challan-invoice-list-search-input');
    const searchForm = document.querySelector('.sales-challan-invoice-list-search-form');
    
    if (searchInput && searchForm) {
        // Auto-submit search after typing stops
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    searchForm.submit();
                }
            }, 500);
        });
        
        // Clear search on Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                searchForm.submit();
            }
        });
    }
}

// Initialize date filters
function initializeDateFilters() {
    const startDateInput = document.querySelector('.sales-challan-invoice-list-start-date');
    const endDateInput = document.querySelector('.sales-challan-invoice-list-end-date');
    const dateForm = document.querySelector('.sales-challan-invoice-list-date-form');
    
    if (startDateInput && endDateInput && dateForm) {
        // Auto-submit when both dates are selected
        function checkAndSubmit() {
            if (startDateInput.value && endDateInput.value) {
                dateForm.submit();
            }
        }
        
        startDateInput.addEventListener('change', checkAndSubmit);
        endDateInput.addEventListener('change', checkAndSubmit);
        
        // Validate date range
        startDateInput.addEventListener('change', function() {
            if (this.value && endDateInput.value && this.value > endDateInput.value) {
                endDateInput.value = this.value;
            }
        });
        
        endDateInput.addEventListener('change', function() {
            if (this.value && startDateInput.value && this.value < startDateInput.value) {
                startDateInput.value = this.value;
            }
        });
    }
}

// Initialize table interactions
function initializeTableFeatures() {
    const tableRows = document.querySelectorAll('.sales-challan-invoice-list-table-row');
    
    tableRows.forEach(row => {
        // Add hover effects and click handlers
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--hover-bg-color, #f8f9fa)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
        
        // Double-click to view details
        row.addEventListener('dblclick', function() {
            const viewBtn = this.querySelector('.sales-challan-invoice-list-view-btn');
            if (viewBtn) {
                viewBtn.click();
            }
        });
    });
}

// Initialize payment buttons
function initializePaymentButtons() {
    const paymentButtons = document.querySelectorAll('.sales-challan-invoice-list-payment-btn');
    
    paymentButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Extract data from onclick attribute or data attributes
            const onclick = this.getAttribute('onclick');
            if (onclick) {
                // Parse the onclick function call
                const match = onclick.match(/showSalesChallanPaymentDialog\('([^']+)',\s*'([^']+)',\s*'([^']+)'\)/);
                if (match) {
                    const [, invoiceId, invoiceNo, balance] = match;
                    showSalesChallanPaymentDialog(invoiceId, invoiceNo, balance);
                }
            }
        });
    });
}

// Initialize pagination
function initializePagination() {
    const paginationLinks = document.querySelectorAll('.sales-challan-invoice-list-pagination-link');
    
    paginationLinks.forEach(link => {
        if (!link.closest('.sales-challan-invoice-list-pagination-disabled')) {
            link.addEventListener('click', function(e) {
                if (this.getAttribute('href') === '#') {
                    e.preventDefault();
                }
            });
        }
    });
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `sales-challan-notification sales-challan-notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Main initialization function
function initializeSalesChallanInvoiceList() {
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSalesChallanInvoiceList);
        return;
    }
    
    try {
        initializePaymentForm();
        initializeModalHandlers();
        initializeKeyboardShortcuts();
        initializeSearchFeatures();
        initializeDateFilters();
        initializeTableFeatures();
        initializePaymentButtons();
        initializePagination();
        
        console.log('Sales Challan Invoice List initialized successfully');
    } catch (error) {
        console.error('Error initializing Sales Challan Invoice List:', error);
    }
}

// Auto-initialize when script loads
initializeSalesChallanInvoiceList();

// Export functions for global access
window.showSalesChallanPaymentDialog = showSalesChallanPaymentDialog;
window.hideSalesChallanPaymentModal = hideSalesChallanPaymentModal;