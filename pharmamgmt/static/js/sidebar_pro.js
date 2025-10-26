// Pharma Sidebar Professional JavaScript
class PharmaSidebarPro {
    constructor() {
        this.sidebar = document.getElementById('pharmaSidebar');
        this.mainContent = document.getElementById('mainContent');
        this.mobileOverlay = document.getElementById('mobileOverlay');
        this.activeSubmenu = null;
        this.activeMenuItem = null;
        this.isCollapsed = false;
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.restoreState();
        this.setupKeyboardShortcuts();
        this.handleResize();
        
        // Add animation classes after initialization
        setTimeout(() => {
            this.sidebar.classList.add('pharma-fade-in');
        }, 100);
    }
    
    setupEventListeners() {
        // Submenu toggle buttons
        const menuButtons = document.querySelectorAll('.pharma-nav-menu-button');
        menuButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const submenuId = button.getAttribute('data-submenu');
                this.toggleSubmenu(submenuId, button);
            });
        });
        
        // Menu item clicks
        const menuItems = document.querySelectorAll('.pharma-nav-link, .pharma-nav-submenu-link');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.setActiveMenuItem(item);
                this.saveState();
                
                // Close sidebar on mobile after selection
                if (this.isMobile) {
                    this.closeMobileSidebar();
                }
            });
        });
        
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }
        
        // Mobile overlay click
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => {
                this.closeMobileSidebar();
            });
        }
        
        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Prevent submenu close when clicking inside
        const submenus = document.querySelectorAll('.pharma-submenu');
        submenus.forEach(submenu => {
            submenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        });
        
        // Close submenus when clicking outside on desktop
        document.addEventListener('click', (e) => {
            if (!this.isMobile && !e.target.closest('.pharma-nav-item')) {
                this.closeAllSubmenus();
            }
        });
    }
    
    toggleSubmenu(submenuId, button) {
        const submenu = document.getElementById(submenuId);
        const navItem = button.closest('.pharma-nav-item');
        const icon = button.querySelector('.pharma-nav-arrow');
        
        if (submenu.classList.contains('hidden')) {
            // Close other submenus first
            if (this.activeSubmenu && this.activeSubmenu !== submenuId) {
                this.closeSubmenu(this.activeSubmenu);
            }
            
            // Open the clicked submenu
            this.openSubmenu(submenuId, button, navItem, icon);
        } else {
            // Close the clicked submenu
            this.closeSubmenu(submenuId, button, navItem, icon);
        }
        
        this.saveState();
    }
    
    openSubmenu(submenuId, button, navItem, icon) {
        const submenu = document.getElementById(submenuId);
        
        submenu.classList.remove('hidden');
        button.setAttribute('aria-expanded', 'true');
        navItem.classList.add('active');
        if (icon) {
            icon.style.transform = 'rotate(180deg)';
            icon.style.opacity = '1';
        }
        
        // Calculate and set max-height for smooth animation
        const submenuHeight = submenu.scrollHeight;
        submenu.style.maxHeight = submenuHeight + 'px';
        
        this.activeSubmenu = submenuId;
    }
    
    closeSubmenu(submenuId, button, navItem, icon) {
        const submenu = document.getElementById(submenuId);
        
        submenu.classList.add('hidden');
        if (button) button.setAttribute('aria-expanded', 'false');
        if (navItem) navItem.classList.remove('active');
        if (icon) {
            icon.style.transform = 'rotate(0deg)';
            icon.style.opacity = '0.7';
        }
        
        submenu.style.maxHeight = '0px';
        
        if (this.activeSubmenu === submenuId) {
            this.activeSubmenu = null;
        }
    }
    
    closeAllSubmenus() {
        const allSubmenus = document.querySelectorAll('.pharma-submenu');
        const allButtons = document.querySelectorAll('.pharma-nav-menu-button');
        const allNavItems = document.querySelectorAll('.pharma-nav-item');
        const allIcons = document.querySelectorAll('.pharma-nav-arrow');
        
        allSubmenus.forEach((menu, index) => {
            if (!menu.classList.contains('hidden')) {
                this.closeSubmenu(
                    menu.id,
                    allButtons[index],
                    allNavItems[index],
                    allIcons[index]
                );
            }
        });
    }
    
    setActiveMenuItem(item) {
        // Remove active class from all menu items
        const allMenuItems = document.querySelectorAll('.pharma-nav-link, .pharma-nav-submenu-link');
        allMenuItems.forEach(menuItem => {
            menuItem.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.classList.add('active');
        this.activeMenuItem = item.getAttribute('data-nav-item') || item.getAttribute('href');
        
        // If it's a submenu item, ensure parent submenu is open
        const submenuItem = item.closest('.pharma-submenu');
        if (submenuItem) {
            const submenuId = submenuItem.id;
            const parentButton = document.querySelector(`[data-submenu="${submenuId}"]`);
            if (parentButton && submenuItem.classList.contains('hidden')) {
                this.toggleSubmenu(submenuId, parentButton);
            }
        }
        
        // Add slide-in animation to active item
        item.classList.add('pharma-slide-in');
        setTimeout(() => {
            item.classList.remove('pharma-slide-in');
        }, 400);
    }
    
    toggleSidebar() {
        if (this.isMobile) {
            this.toggleMobileSidebar();
        } else {
            this.toggleCollapse();
        }
    }
    
    toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            this.sidebar.classList.add('collapsed');
            this.mainContent.classList.add('sidebar-collapsed');
        } else {
            this.sidebar.classList.remove('collapsed');
            this.mainContent.classList.remove('sidebar-collapsed');
        }
        
        this.saveState();
    }
    
    toggleMobileSidebar() {
        if (this.sidebar.classList.contains('mobile-open')) {
            this.closeMobileSidebar();
        } else {
            this.openMobileSidebar();
        }
    }
    
    openMobileSidebar() {
        this.sidebar.classList.add('mobile-open');
        this.mobileOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeMobileSidebar() {
        this.sidebar.classList.remove('mobile-open');
        this.mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile && !this.isMobile) {
            // Switching from mobile to desktop
            this.closeMobileSidebar();
            this.mainContent.classList.remove('sidebar-mobile');
        } else if (!wasMobile && this.isMobile) {
            // Switching from desktop to mobile
            this.mainContent.classList.add('sidebar-mobile');
        }
    }
    
    saveState() {
        const state = {
            activeSubmenu: this.activeSubmenu,
            activeMenuItem: this.activeMenuItem,
            isCollapsed: this.isCollapsed,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem('pharmaSidebarState', JSON.stringify(state));
        } catch (e) {
            console.warn('Could not save sidebar state to localStorage:', e);
        }
    }
    
    restoreState() {
        try {
            const savedState = localStorage.getItem('pharmaSidebarState');
            
            if (savedState) {
                const state = JSON.parse(savedState);
                
                // Restore collapsed state
                if (state.isCollapsed && !this.isMobile) {
                    this.toggleCollapse();
                }
                
                // Restore active submenu if it exists
                if (state.activeSubmenu) {
                    const submenu = document.getElementById(state.activeSubmenu);
                    const button = document.querySelector(`[data-submenu="${state.activeSubmenu}"]`);
                    
                    if (submenu && button && !submenu.classList.contains('hidden')) {
                        this.openSubmenu(
                            state.activeSubmenu,
                            button,
                            button.closest('.pharma-nav-item'),
                            button.querySelector('.pharma-nav-arrow')
                        );
                    }
                }
                
                // Restore active menu item if it exists
                if (state.activeMenuItem) {
                    let menuItem = document.querySelector(`[data-nav-item="${state.activeMenuItem}"]`) ||
                                 document.querySelector(`[href="${state.activeMenuItem}"]`);
                    
                    if (menuItem) {
                        this.setActiveMenuItem(menuItem);
                    }
                }
            }
        } catch (e) {
            console.warn('Error restoring sidebar state:', e);
            this.clearState();
        }
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+SI for Quick Invoice+Products
            if (e.ctrlKey && e.key.toLowerCase() === 's') {
                e.preventDefault();
                const quickInvoiceLink = document.getElementById('quickInvoiceLink');
                if (quickInvoiceLink) {
                    quickInvoiceLink.click();
                }
            }
            
            // Escape key to close all submenus or mobile sidebar
            if (e.key === 'Escape') {
                if (this.isMobile && this.sidebar.classList.contains('mobile-open')) {
                    this.closeMobileSidebar();
                } else {
                    this.closeAllSubmenus();
                }
            }
            
            // Ctrl+B to toggle sidebar (desktop only)
            if (e.ctrlKey && e.key.toLowerCase() === 'b' && !this.isMobile) {
                e.preventDefault();
                this.toggleCollapse();
            }
        });
    }
    
    // Public methods for external control
    openSubmenuById(submenuId) {
        const button = document.querySelector(`[data-submenu="${submenuId}"]`);
        if (button) {
            this.toggleSubmenu(submenuId, button);
        }
    }
    
    setActiveItemById(itemId) {
        const menuItem = document.querySelector(`[data-nav-item="${itemId}"]`);
        if (menuItem) {
            this.setActiveMenuItem(menuItem);
        }
    }
    
    setActiveItemByHref(href) {
        const menuItem = document.querySelector(`[href="${href}"]`);
        if (menuItem) {
            this.setActiveMenuItem(menuItem);
        }
    }
    
    clearState() {
        try {
            localStorage.removeItem('pharmaSidebarState');
        } catch (e) {
            console.warn('Could not clear sidebar state:', e);
        }
        
        this.activeSubmenu = null;
        this.activeMenuItem = null;
        this.isCollapsed = false;
        
        // Reset UI
        this.closeAllSubmenus();
        const allMenuItems = document.querySelectorAll('.pharma-nav-link, .pharma-nav-submenu-link');
        allMenuItems.forEach(item => item.classList.remove('active'));
        
        if (this.sidebar.classList.contains('collapsed')) {
            this.toggleCollapse();
        }
    }
    
    // Utility method to check if sidebar is open (mobile)
    isSidebarOpen() {
        return this.isMobile ? 
            this.sidebar.classList.contains('mobile-open') : 
            !this.isCollapsed;
    }
    
    // Method to refresh sidebar state (useful after dynamic content changes)
    refresh() {
        this.saveState();
    }
}

// Initialize sidebar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.pharmaSidebar = new PharmaSidebarPro();
    
    // Add global error handler for sidebar
    window.addEventListener('error', (e) => {
        if (e.target && (e.target.classList.contains('pharma-nav-link') || 
                         e.target.classList.contains('pharma-nav-menu-button') ||
                         e.target.closest('.pharma-sidebar-container'))) {
            console.error('Sidebar interaction error:', e.error);
        }
    });
});

// Global functions for backward compatibility
function toggleSubmenu(submenuId) {
    if (window.pharmaSidebar) {
        const button = document.querySelector(`[data-submenu="${submenuId}"]`);
        if (button) {
            window.pharmaSidebar.toggleSubmenu(submenuId, button);
        }
    }
}

// Example: Programmatically open returns submenu and set purchase returns as active
function openReturnsWithPurchaseReturns() {
    if (window.pharmaSidebar) {
        // Open returns submenu
        window.pharmaSidebar.openSubmenuById('returnsSubmenu');
        
        // Set purchase returns as active after a short delay to ensure submenu is open
        setTimeout(() => {
            window.pharmaSidebar.setActiveItemById('purchase-returns');
        }, 100);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PharmaSidebarPro;
}