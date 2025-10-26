// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mainContentArea = document.querySelector('.main-content-area');

    // Toggle sidebar
    function toggleSidebar() {
        const isOpen = sidebar.classList.contains('active');
        
        if (isOpen) {
            sidebar.classList.remove('active');
            if (mainContentArea) mainContentArea.classList.remove('sidebar-open');
        } else {
            sidebar.classList.add('active');
            if (mainContentArea) mainContentArea.classList.add('sidebar-open');
        }
    }

    // Event listeners
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Keyboard shortcuts
    let keySequence = [];
    let sequenceTimeout;
    
    document.addEventListener('keydown', function(e) {
        // Alt+Q for sidebar toggle
        if (e.altKey && (e.key === 'q' || e.key === 'Q')) {
            e.preventDefault();
            toggleSidebar();
            return false;
        }
        
        // Alt+P+I for Purchase Invoices (only if not part of reports sequence)
        if (e.altKey && (e.key === 'p' || e.key === 'P') && !keySequence.includes('r')) {
            keySequence = ['p'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        if (keySequence.includes('p') && e.altKey && (e.key === 'i' || e.key === 'I')) {
            e.preventDefault();
            window.location.href = '/invoices';
            keySequence = [];
            return false;
        }
        
        // Alt+P+N for New Invoice + Products
        if (keySequence.includes('p') && e.altKey && (e.key === 'n' || e.key === 'N')) {
            e.preventDefault();
            window.location.href = '/invoices/add-with-products/';
            keySequence = [];
            return false;
        }
        
        // Alt+P+L for Product List
        if (keySequence.includes('p') && e.altKey && (e.key === 'l' || e.key === 'L')) {
            e.preventDefault();
            window.location.href = '/products/';
            keySequence = [];
            return false;
        }
        
        // Alt+P+R for Purchase Returns
        if (keySequence.includes('p') && e.altKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            window.location.href = '/purchase-returns/';
            keySequence = [];
            return false;
        }
        
        // Sales section shortcuts are now handled by the Alt+S logic above
        
        if (keySequence.includes('s') && e.altKey && (e.key === 'i' || e.key === 'I')) {
            e.preventDefault();
            window.location.href = '/sales';
            keySequence = [];
            return false;
        }
        
        if (keySequence.includes('s') && e.altKey && (e.key === 'n' || e.key === 'N')) {
            e.preventDefault();
            window.location.href = '/sales/add-with-products/';
            keySequence = [];
            return false;
        }
        
        // Alt+S+R for Sales Returns
        if (keySequence.includes('s') && e.altKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            window.location.href = '/sales-returns';
            keySequence = [];
            return false;
        }
        
        // Alt+B+I for Batch-wise Inventory
        if (e.altKey && (e.key === 'b' || e.key === 'B')) {
            keySequence = ['b'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        if (keySequence.includes('b') && e.altKey && (e.key === 'i' || e.key === 'I')) {
            e.preventDefault();
            window.location.href = '/reports/inventory/batch/';
            keySequence = [];
            return false;
        }
        
        // Alt+B+R for Batch Rates
        if (keySequence.includes('b') && e.altKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            window.location.href = '/rates/';
            keySequence = [];
            return false;
        }
        
        // Alt+E+I for Expiry/Date-wise Inventory
        if (e.altKey && (e.key === 'e' || e.key === 'E')) {
            keySequence = ['e'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        if (keySequence.includes('e') && e.altKey && (e.key === 'i' || e.key === 'I')) {
            e.preventDefault();
            window.location.href = '/reports/inventory/expiry/';
            keySequence = [];
            return false;
        }
        
        // Alt+S for Supplier (direct shortcut when no sequence)
        if (e.altKey && (e.key === 's' || e.key === 'S') && keySequence.length === 0) {
            // Check if this is start of a sequence or direct supplier access
            keySequence = ['s'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => {
                // If no second key pressed, go to supplier page
                if (keySequence.includes('s')) {
                    window.location.href = '/suppliers/';
                }
                keySequence = [];
            }, 800); // Shorter timeout for direct access
            e.preventDefault();
            return false;
        }
        
        // Handle Alt+S when it's part of reports sequence (Alt+R+S)
        if (keySequence.includes('r') && e.altKey && (e.key === 's' || e.key === 'S')) {
            // This is handled above in Alt+R+S section
            return;
        }
        
        // Alt+C for Customer
        if (e.altKey && (e.key === 'c' || e.key === 'C')) {
            e.preventDefault();
            window.location.href = '/customers/';
            return false;
        }
        
        // Alt+R for Reports Section
        if (e.altKey && (e.key === 'r' || e.key === 'R') && keySequence.length === 0) {
            keySequence = ['r'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        // Alt+R+S for Sales Reports
        if (keySequence.includes('r') && e.altKey && (e.key === 's' || e.key === 'S')) {
            e.preventDefault();
            window.location.href = '/reports/sales/';
            keySequence = [];
            return false;
        }
        
        // Alt+R+P for Purchase Reports (prioritize over other P shortcuts)
        if (keySequence.includes('r') && e.altKey && (e.key === 'p' || e.key === 'P')) {
            e.preventDefault();
            console.log('Alt+R+P triggered - going to purchase reports');
            window.location.href = '/reports/purchase/';
            keySequence = [];
            return false;
        }
        
        // Alt+R+F for Financial Reports
        if (keySequence.includes('r') && e.altKey && (e.key === 'f' || e.key === 'F')) {
            e.preventDefault();
            window.location.href = '/reports/financial/';
            keySequence = [];
            return false;
        }
        
        // Alt+D for Dashboard (direct shortcut)
        if (e.altKey && (e.key === 'd' || e.key === 'D') && keySequence.length === 0) {
            e.preventDefault();
            window.location.href = '/';
            return false;
        }
        
        // Alt+F for Finance Section
        if (e.altKey && (e.key === 'f' || e.key === 'F') && keySequence.length === 0) {
            keySequence = ['f'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        // Alt+F+P for Financial Payment
        if (keySequence.includes('f') && e.altKey && (e.key === 'p' || e.key === 'P')) {
            e.preventDefault();
            window.location.href = '/payments/';
            keySequence = [];
            return false;
        }
        
        // Alt+S+P for Sales Receipt
        if (keySequence.includes('s') && e.altKey && (e.key === 'p' || e.key === 'P')) {
            e.preventDefault();
            window.location.href = '/receipts/';
            keySequence = [];
            return false;
        }
        
        // Alt+A for Admin Section
        if (e.altKey && (e.key === 'a' || e.key === 'A') && keySequence.length === 0) {
            keySequence = ['a'];
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => keySequence = [], 1500);
            e.preventDefault();
            return false;
        }
        
        // Alt+A+D for Add User
        if (keySequence.includes('a') && e.altKey && (e.key === 'd' || e.key === 'D')) {
            e.preventDefault();
            window.location.href = '/register/';
            keySequence = [];
            return false;
        }
        
        // Alt+P+D for Pharmacy Details
        if (keySequence.includes('p') && e.altKey && (e.key === 'd' || e.key === 'D')) {
            e.preventDefault();
            window.location.href = '/pharmacy-details/';
            keySequence = [];
            return false;
        }
        
        // Alt+P+N for New Invoice with Products
        if (keySequence.includes('p') && e.altKey && (e.key === 'n' || e.key === 'N')) {
            e.preventDefault();
            window.location.href = '/add-invoice-with-products/';
            keySequence = [];
            return false;
        }
        
        // Alt+P+I for Purchase Invoices List
        if (keySequence.includes('p') && e.altKey && (e.key === 'i' || e.key === 'I')) {
            e.preventDefault();
            window.location.href = '/invoices/';
            keySequence = [];
            return false;
        }
        
        // Alt+L for Logout
        if (e.altKey && (e.key === 'l' || e.key === 'L')) {
            e.preventDefault();
            window.location.href = '/logout/';
            return false;
        }
        
        // Alt+I for All Product Inventory
        if (e.altKey && (e.key === 'i' || e.key === 'I') && !keySequence.includes('p') && !keySequence.includes('s') && !keySequence.includes('b') && !keySequence.includes('d') && !keySequence.includes('r') && !keySequence.includes('f') && !keySequence.includes('e') && !keySequence.includes('a')) {
            e.preventDefault();
            window.location.href = '/inventory';
            return false;
        }
    });

    // Keep active navigation state and sidebar open
    function setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link, .nav-submenu-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
                
                // If it's a submenu link, keep parent submenu open
                const parentSubmenu = link.closest('.submenu');
                if (parentSubmenu) {
                    parentSubmenu.classList.remove('hidden');
                    const parentButton = parentSubmenu.previousElementSibling;
                    parentButton.setAttribute('aria-expanded', 'true');
                    parentButton.classList.add('active');
                }
            }
        });
    }

    // Prevent sidebar from closing when clicking navigation links
    const allNavLinks = document.querySelectorAll('.nav-link, .nav-submenu-link');
    allNavLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't close sidebar when navigating
            // Sidebar will remain open until user manually closes it
        });
    });

    // Initialize active navigation
    setActiveNavigation();
    
    // Remove existing shortcut badges and add correct ones
    removeExistingBadges();
    addShortcutBadges();
});

// Submenu toggle functionality (global function for onclick)
function toggleSubmenu(submenuId) {
    const submenu = document.getElementById(submenuId);
    const button = submenu.previousElementSibling;
    
    if (submenu.classList.contains('hidden')) {
        // Close all other submenus
        document.querySelectorAll('.submenu').forEach(menu => {
            if (menu.id !== submenuId) {
                menu.classList.add('hidden');
            }
        });
        document.querySelectorAll('.nav-menu-button').forEach(btn => {
            if (btn !== button) {
                btn.setAttribute('aria-expanded', 'false');
                btn.classList.remove('active');
            }
        });
        
        // Open clicked submenu
        submenu.classList.remove('hidden');
        button.setAttribute('aria-expanded', 'true');
        button.classList.add('active');
    } else {
        submenu.classList.add('hidden');
        button.setAttribute('aria-expanded', 'false');
        button.classList.remove('active');
    }
    
    // Keep sidebar open when toggling submenus
    const sidebar = document.getElementById('sidebar');
    const mainContentArea = document.querySelector('.main-content-area');
    if (sidebar && !sidebar.classList.contains('active')) {
        sidebar.classList.add('active');
        if (mainContentArea) mainContentArea.classList.add('sidebar-open');
    }
}

// Remove existing shortcut badges
function removeExistingBadges() {
    // Remove any existing badges (including Ctrl+S ones)
    const existingBadges = document.querySelectorAll('.shortcut-badge, .badge, [class*="ctrl"], [class*="shortcut"]');
    existingBadges.forEach(badge => {
        if (badge.textContent.includes('Ctrl') || badge.textContent.includes('Alt')) {
            badge.remove();
        }
    });
    
    // Also remove any inline style badges
    const allElements = document.querySelectorAll('*');
    allElements.forEach(element => {
        if (element.textContent && element.textContent.includes('Ctrl+S')) {
            // If it's a small badge-like element, remove it
            if (element.tagName === 'SPAN' && element.style.fontSize && element.style.fontSize.includes('10px')) {
                element.remove();
            }
        }
    });
}

// Add keyboard shortcut badges to navigation items
function addShortcutBadges() {
    const shortcuts = {
        // Navigation shortcuts
        'Dashboard': 'Alt+D',
        'Customer': 'Alt+C',
        'Supplier': 'Alt+S',
        'Logout': 'Alt+L',
        
        // Purchase section
        'Invoices': 'Alt+P+I',
        'New Invoice': 'Alt+P+N',
        'New Invoice + Products': 'Alt+P+N',
        'Add with Products': 'Alt+P+N',
        'Products': 'Alt+P+L',
        'Product List': 'Alt+P+L',
        'Purchase Return': 'Alt+P+R',
        'Pharmacy Details': 'Alt+P+D',
        
        // Sales section
        'Sales': 'Alt+S+I',
        'Quick Invoice': 'Alt+S+N',
        'Sales Return': 'Alt+S+R',
        'Receipt': 'Alt+S+P',
        
        // Inventory section
        'Inventory': 'Alt+I',
        'Batch': 'Alt+B+I',
        'Expiry': 'Alt+E+I',
        'Date wise': 'Alt+E+I',
        'Date Wise': 'Alt+E+I',
        'Rates': 'Alt+B+R',
        
        // Reports section
        'Sales Report': 'Alt+R+S',
        'Purchase Report': 'Alt+R+P',
        'Purchase Reports': 'Alt+R+P',
        'Financial Report': 'Alt+R+F',
        
        // Finance section
        'Payment': 'Alt+F+P',
        
        // Admin section
        'Add User': 'Alt+A+D'
    };
    
    // Add badges to navigation links
    Object.keys(shortcuts).forEach(linkText => {
        const links = document.querySelectorAll('.nav-link, .nav-submenu-link');
        links.forEach(link => {
            const linkTextContent = link.textContent.trim().toLowerCase();
            const searchText = linkText.toLowerCase();
            
            // Check if link text contains the search text or vice versa
            if (linkTextContent.includes(searchText) || searchText.includes(linkTextContent)) {
                // Avoid duplicate badges
                if (!link.querySelector('.shortcut-badge')) {
                    const badge = document.createElement('span');
                    badge.className = 'shortcut-badge';
                    badge.textContent = shortcuts[linkText];
                    badge.style.cssText = `
                        background: #007bff;
                        color: white;
                        font-size: 10px;
                        padding: 2px 6px;
                        border-radius: 10px;
                        margin-left: 8px;
                        font-weight: normal;
                        opacity: 0.8;
                        display: inline-block;
                    `;
                    link.appendChild(badge);
                }
            }
        });
    });
}