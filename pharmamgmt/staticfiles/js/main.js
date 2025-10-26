// Main JavaScript for Pharmacy Management System
document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar on mobile
    const sidebarToggler = document.querySelector('#sidebarToggle');
    if (sidebarToggler) {
        sidebarToggler.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('active');
            document.querySelector('.content').classList.toggle('active');
        });
    }

    // Expand/collapse submenu items
    const submenuTogglers = document.querySelectorAll('.has-submenu > a');
    submenuTogglers.forEach(toggler => {
        toggler.addEventListener('click', function(e) {
            e.preventDefault();
            this.parentElement.classList.toggle('active');
        });
    });

    // Tooltips initialization
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Note: Date inputs now use global DDMM formatter instead of flatpickr
    // The date-formatter.js handles all date input formatting globally
    console.log('Date inputs will use DDMM format with auto-year completion');

    // DataTables initialization for tables
    const dataTables = document.querySelectorAll('.datatable');
    dataTables.forEach(table => {
        if (typeof $.fn.DataTable !== 'undefined') {
            $(table).DataTable({
                responsive: true,
                language: {
                    search: "_INPUT_",
                    searchPlaceholder: "Search...",
                }
            });
        }
    });

    // Delete actions handled by individual page scripts
    // No global confirm dialog needed

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Dynamic form fields (add/remove)
    const addFieldButton = document.querySelector('.add-field-btn');
    if (addFieldButton) {
        addFieldButton.addEventListener('click', function() {
            const fieldContainer = document.querySelector('.dynamic-fields');
            const fieldRow = document.querySelector('.field-row').cloneNode(true);
            const inputs = fieldRow.querySelectorAll('input, select');
            
            // Clear values and increment indices
            inputs.forEach(input => {
                input.value = '';
                if (input.name) {
                    const newIndex = document.querySelectorAll('.field-row').length;
                    input.name = input.name.replace(/\[\d+\]/, `[${newIndex}]`);
                }
            });
            
            // Add delete button functionality
            const deleteBtn = fieldRow.querySelector('.remove-field-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', function() {
                    fieldRow.remove();
                });
            }
            
            fieldContainer.appendChild(fieldRow);
        });
    }

    // Implement search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const searchables = document.querySelectorAll('.searchable');
            
            searchables.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Auto-calculate totals in invoices
    const calculateTotals = function() {
        // Get all quantity inputs
        const qtyInputs = document.querySelectorAll('.qty-input');
        let grandTotal = 0;
        
        qtyInputs.forEach(input => {
            const row = input.closest('tr');
            const qty = parseFloat(input.value) || 0;
            const rate = parseFloat(row.querySelector('.rate-input').value) || 0;
            const discount = parseFloat(row.querySelector('.discount-input').value) || 0;
            
            // Calculate line total
            const total = (qty * rate) * (1 - discount / 100);
            row.querySelector('.total-input').value = total.toFixed(2);
            
            // Add to grand total
            grandTotal += total;
        });
        
        // Update grand total
        const grandTotalElement = document.getElementById('grandTotal');
        if (grandTotalElement) {
            grandTotalElement.textContent = grandTotal.toFixed(2);
        }
    };
    
    // Add event listeners to invoice inputs
    const invoiceInputs = document.querySelectorAll('.qty-input, .rate-input, .discount-input');
    invoiceInputs.forEach(input => {
        input.addEventListener('change', calculateTotals);
        input.addEventListener('keyup', calculateTotals);
    });
    
    // Initialize calculation
    if (invoiceInputs.length > 0) {
        calculateTotals();
    }
    
    // Ensure date formatter is initialized for any dynamically loaded content
    if (window.DateFormatter && typeof window.DateFormatter.initializeInputs === 'function') {
        setTimeout(() => {
            window.DateFormatter.initializeInputs();
        }, 500);
    }

    // Handle product search in purchase/sales forms
    const productSearchInput = document.getElementById('productSearch');
    if (productSearchInput) {
        productSearchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            
            // Make AJAX request to search products
            if (searchTerm.length >= 3) {
                fetch(`/products/search/?q=${searchTerm}`)
                    .then(response => response.json())
                    .then(data => {
                        const resultsContainer = document.getElementById('searchResults');
                        resultsContainer.innerHTML = '';
                        
                        if (data.length > 0) {
                            data.forEach(product => {
                                const div = document.createElement('div');
                                div.classList.add('search-result');
                                div.textContent = `${product.product_name} (${product.product_company})`;
                                div.addEventListener('click', function() {
                                    document.getElementById('productId').value = product.id;
                                    document.getElementById('productName').value = product.product_name;
                                    document.getElementById('productCompany').value = product.product_company;
                                    document.getElementById('productMRP').value = product.mrp;
                                    resultsContainer.innerHTML = '';
                                    productSearchInput.value = '';
                                });
                                resultsContainer.appendChild(div);
                            });
                        } else {
                            const div = document.createElement('div');
                            div.classList.add('no-results');
                            div.textContent = 'No products found';
                            resultsContainer.appendChild(div);
                        }
                    });
            }
        });
    }
});