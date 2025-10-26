// Theme Toggle Functionality
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Set initial theme
        this.setTheme(this.currentTheme);
        
        // Create theme toggle button
        this.createThemeToggle();
        
        // Add event listeners
        this.addEventListeners();
        
        // Add smooth transitions
        this.addTransitions();
    }

    createThemeToggle() {
        const navbar = document.querySelector('.top-navbar .user-menu');
        if (navbar) {
            const themeToggle = document.createElement('button');
            themeToggle.className = 'theme-toggle';
            themeToggle.innerHTML = this.getThemeIcon();
            themeToggle.setAttribute('aria-label', 'Toggle theme');
            themeToggle.setAttribute('title', 'Toggle Dark/Light Mode');
            
            // Insert before user menu
            navbar.insertBefore(themeToggle, navbar.firstChild);
        }
    }

    getThemeIcon() {
        return this.currentTheme === 'light' 
            ? '<i class="fas fa-moon"></i>' 
            : '<i class="fas fa-sun"></i>';
    }

    addEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle')) {
                this.toggleTheme();
            }
        });

        // Keyboard shortcut: Ctrl + Shift + T
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(this.currentTheme);
        this.updateThemeIcon();
        this.saveTheme();
        this.animateToggle();
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.content = theme === 'dark' ? '#0f172a' : '#ffffff';
    }

    updateThemeIcon() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = this.getThemeIcon();
        }
    }

    saveTheme() {
        localStorage.setItem('theme', this.currentTheme);
    }

    animateToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.style.transform = 'scale(0.8) rotate(180deg)';
            setTimeout(() => {
                themeToggle.style.transform = 'scale(1) rotate(0deg)';
            }, 150);
        }

        // Add ripple effect
        this.createRippleEffect(themeToggle);
    }

    createRippleEffect(element) {
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(102, 126, 234, 0.3);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            top: 50%;
            left: 50%;
            width: 100px;
            height: 100px;
            margin-left: -50px;
            margin-top: -50px;
        `;

        element.style.position = 'relative';
        element.appendChild(ripple);

        // Add ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    addTransitions() {
        // Add smooth transitions to all elements
        const style = document.createElement('style');
        style.textContent = `
            * {
                transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                           border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                           color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                           box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Auto theme based on system preference
    enableAutoTheme() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleChange = (e) => {
                if (!localStorage.getItem('theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                    this.updateThemeIcon();
                }
            };

            mediaQuery.addListener(handleChange);
            handleChange(mediaQuery);
        }
    }
}

// Enhanced animations and effects
class UIEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.addScrollAnimations();
        this.addHoverEffects();
        this.addLoadingAnimations();
        this.addParticleEffect();
    }

    addScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe dashboard cards and form cards
        document.querySelectorAll('.dashboard-card, .form-card, .data-table').forEach(el => {
            observer.observe(el);
        });
    }

    addHoverEffects() {
        // Add magnetic effect to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                e.target.style.transform = 'translateY(-2px) scale(1.02)';
            });

            btn.addEventListener('mouseleave', (e) => {
                e.target.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Add glow effect to cards on hover
        document.querySelectorAll('.dashboard-card').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                e.target.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.15)';
            });

            card.addEventListener('mouseleave', (e) => {
                e.target.style.boxShadow = '';
            });
        });
    }

    addLoadingAnimations() {
        // Add loading state to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                    submitBtn.disabled = true;

                    // Re-enable after 3 seconds (fallback)
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 3000);
                }
            });
        });
    }

    addParticleEffect() {
        // Add subtle particle effect to sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            for (let i = 0; i < 5; i++) {
                const particle = document.createElement('div');
                particle.style.cssText = `
                    position: absolute;
                    width: 4px;
                    height: 4px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    animation: float ${3 + Math.random() * 4}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 2}s;
                    top: ${Math.random() * 100}%;
                    left: ${Math.random() * 100}%;
                    pointer-events: none;
                `;
                sidebar.appendChild(particle);
            }

            // Add floating animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes float {
                    0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.1; }
                    50% { transform: translateY(-20px) rotate(180deg); opacity: 0.3; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const themeManager = new ThemeManager();
    const uiEnhancements = new UIEnhancements();
    
    // Enable auto theme detection
    themeManager.enableAutoTheme();
    
    console.log('🎨 Beautiful theme system initialized!');
});

// Export for use in other scripts
window.ThemeManager = ThemeManager;