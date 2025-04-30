document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }
    
    // Dropdown submenus
    const dropdownItems = document.querySelectorAll('.nav-link[data-bs-toggle="collapse"]');
    
    dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Only prevent default if it's not Bootstrap's collapse functionality
            if (!e.target.classList.contains('nav-link')) {
                e.preventDefault();
            }
        });
    });

    // Product image preview on product form
    const productImageInput = document.getElementById('id_product_image');
    const productImagePreview = document.getElementById('product-image-preview');
    
    if (productImageInput && productImagePreview) {
        productImageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    productImagePreview.src = e.target.result;
                    productImagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Sales form dynamic product selection
    const productSelect = document.getElementById('id_productid');
    if (productSelect) {
        productSelect.addEventListener('change', function() {
            fetchProductInfo(this.value);
        });
    }
    
    // Rate selection toggle in sales form
    const rateSelect = document.getElementById('id_rate_applied');
    const customRateField = document.getElementById('id_sale_rate');
    
    if (rateSelect && customRateField) {
        rateSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customRateField.readOnly = false;
                customRateField.focus();
            } else {
                customRateField.readOnly = true;
            }
        });
    }
    
    // Calculation logic for purchase form
    setupPurchaseFormCalculations();
    
    // Calculation logic for sales form
    setupSalesFormCalculations();
});

// Function to fetch product information via AJAX
function fetchProductInfo(productId) {
    if (!productId) return;
    
    fetch(`/api/product-info/?product_id=${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // For purchase form
                if (document.getElementById('id_product_purchase_rate')) {
                    document.getElementById('product_name_display').textContent = data.product_name;
                    document.getElementById('product_company_display').textContent = data.product_company;
                    document.getElementById('product_packing_display').textContent = data.product_packing;
                }
                
                // For sales form
                if (document.getElementById('id_sale_rate')) {
                    document.getElementById('product_name_display').textContent = data.product_name;
                    document.getElementById('product_company_display').textContent = data.product_company;
                    document.getElementById('product_packing_display').textContent = data.product_packing;
                    
                    const rateSelect = document.getElementById('id_rate_applied');
                    const saleRateInput = document.getElementById('id_sale_rate');
                    
                    if (rateSelect.value === 'A') {
                        saleRateInput.value = data.rate_A;
                    } else if (rateSelect.value === 'B') {
                        saleRateInput.value = data.rate_B;
                    } else if (rateSelect.value === 'C') {
                        saleRateInput.value = data.rate_C;
                    }
                }
            } else {
                console.error("Failed to load product data");
            }
        })
        .catch(error => {
            console.error("Error fetching product data:", error);
        });
}

// Setup calculations for the purchase form
function setupPurchaseFormCalculations() {
    const purchaseForm = document.getElementById('purchase-form');
    
    if (purchaseForm) {
        const quantityInput = document.getElementById('id_product_quantity');
        const rateInput = document.getElementById('id_product_purchase_rate');
        const schemeInput = document.getElementById('id_product_scheme');
        const discountInput = document.getElementById('id_product_discount_got');
        const igstInput = document.getElementById('id_IGST');
        const calculationModeSelect = document.getElementById('id_purchase_calculation_mode');
        const totalAmountDisplay = document.getElementById('total_amount_display');
        
        const updateTotalAmount = function() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const rate = parseFloat(rateInput.value) || 0;
            const scheme = parseFloat(schemeInput.value) || 0;
            const igst = parseFloat(igstInput.value) || 0;
            
            let discount = parseFloat(discountInput.value) || 0;
            if (calculationModeSelect.value === 'perc') {
                discount = (rate * quantity * discount) / 100;
            }
            
            const subtotal = rate * quantity;
            const total = subtotal - discount + (subtotal * igst / 100);
            
            if (totalAmountDisplay) {
                totalAmountDisplay.textContent = total.toFixed(2);
            }
        };
        
        // Add event listeners to all inputs
        [quantityInput, rateInput, schemeInput, discountInput, igstInput, calculationModeSelect].forEach(input => {
            if (input) {
                input.addEventListener('input', updateTotalAmount);
                input.addEventListener('change', updateTotalAmount);
            }
        });
        
        // Initial calculation
        updateTotalAmount();
    }
}

// Setup calculations for the sales form
function setupSalesFormCalculations() {
    const salesForm = document.getElementById('sales-form');
    
    if (salesForm) {
        const quantityInput = document.getElementById('id_sale_quantity');
        const rateInput = document.getElementById('id_sale_rate');
        const schemeInput = document.getElementById('id_sale_scheme');
        const discountInput = document.getElementById('id_sale_discount');
        const igstInput = document.getElementById('id_sale_igst');
        const calculationModeSelect = document.getElementById('id_sale_calculation_mode');
        const totalAmountDisplay = document.getElementById('total_amount_display');
        
        const updateTotalAmount = function() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const rate = parseFloat(rateInput.value) || 0;
            const scheme = parseFloat(schemeInput.value) || 0;
            const igst = parseFloat(igstInput.value) || 0;
            
            let discount = parseFloat(discountInput.value) || 0;
            if (calculationModeSelect.value === 'perc') {
                discount = (rate * quantity * discount) / 100;
            }
            
            const subtotal = rate * quantity;
            const total = subtotal - discount + (subtotal * igst / 100);
            
            if (totalAmountDisplay) {
                totalAmountDisplay.textContent = total.toFixed(2);
            }
        };
        
        // Add event listeners to all inputs
        [quantityInput, rateInput, schemeInput, discountInput, igstInput, calculationModeSelect].forEach(input => {
            if (input) {
                input.addEventListener('input', updateTotalAmount);
                input.addEventListener('change', updateTotalAmount);
            }
        });
        
        // Initial calculation
        updateTotalAmount();
    }
}