/**
 * Product Search Autocomplete with Supplier/Company Sorting
 * Provides real-time search suggestions and sorting functionality
 */

class ProductSearchAutocomplete {
    constructor(searchInputId, suggestionsContainerId, sortSelectId) {
        this.searchInput = document.getElementById(searchInputId);
        this.suggestionsContainer = document.getElementById(suggestionsContainerId);
        this.sortSelect = document.getElementById(sortSelectId);
        this.currentFocus = -1;
        this.suggestions = [];
        this.debounceTimer = null;
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        // Create suggestions container if it doesn't exist
        if (!this.suggestionsContainer) {
            this.createSuggestionsContainer();
        }
        
        // Bind events
        this.bindEvents();
        
        // Initialize sorting if sort select exists
        if (this.sortSelect) {
            this.initSorting();
        }
    }
    
    createSuggestionsContainer() {
        this.suggestionsContainer = document.createElement('div');
        this.suggestionsContainer.id = 'search-suggestions';
        this.suggestionsContainer.className = 'search-suggestions-container';
        this.searchInput.parentNode.appendChild(this.suggestionsContainer);
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });
        
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.length > 0) {
                this.showSuggestions();
            }
        });
        
        // Click outside to close suggestions
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }
    
    initSorting() {
        this.sortSelect.addEventListener('change', (e) => {
            this.handleSortChange(e.target.value);
        });
    }
    
    handleInput(value) {
        clearTimeout(this.debounceTimer);
        
        if (value.length < 1) {
            this.hideSuggestions();
            return;
        }
        
        // Reduce debounce time for more responsive search
        const debounceTime = value.length === 1 ? 500 : 200;
        
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(value);
        }, debounceTime);
    }
    
    async fetchSuggestions(query) {
        try {
            // Show loading state
            this.showLoading();
            
            const response = await fetch(`/api/product-search-suggestions/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                // Sort suggestions by relevance to current query
                this.suggestions = this.sortByRelevance(data.suggestions, query);
                this.renderSuggestions();
            } else {
                this.showNoResults();
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.showError();
        }
    }
    
    sortByRelevance(suggestions, query) {
        const queryLower = query.toLowerCase();
        
        return suggestions.sort((a, b) => {
            const aName = a.product_name.toLowerCase();
            const bName = b.product_name.toLowerCase();
            const aCompany = a.product_company.toLowerCase();
            const bCompany = b.product_company.toLowerCase();
            
            // Priority scoring system
            let aScore = 0;
            let bScore = 0;
            
            // Exact match gets highest priority
            if (aName === queryLower) aScore += 1000;
            if (bName === queryLower) bScore += 1000;
            
            // Starts with query gets high priority
            if (aName.startsWith(queryLower)) aScore += 500;
            if (bName.startsWith(queryLower)) bScore += 500;
            
            // Company name starts with query
            if (aCompany.startsWith(queryLower)) aScore += 300;
            if (bCompany.startsWith(queryLower)) bScore += 300;
            
            // Contains query in name
            if (aName.includes(queryLower)) aScore += 200;
            if (bName.includes(queryLower)) bScore += 200;
            
            // Contains query in company
            if (aCompany.includes(queryLower)) aScore += 100;
            if (bCompany.includes(queryLower)) bScore += 100;
            
            // Stock availability bonus
            if (a.current_stock > 0) aScore += 50;
            if (b.current_stock > 0) bScore += 50;
            
            // Higher stock gets slight preference
            aScore += Math.min(a.current_stock, 10);
            bScore += Math.min(b.current_stock, 10);
            
            return bScore - aScore;
        });
    }
    
    showLoading() {
        this.suggestionsContainer.innerHTML = '<div class="suggestion-loading">Searching...</div>';
        this.showSuggestions();
    }
    
    showNoResults() {
        this.suggestionsContainer.innerHTML = '<div class="suggestion-no-results">No products found</div>';
        this.showSuggestions();
    }
    
    showError() {
        this.suggestionsContainer.innerHTML = '<div class="suggestion-error">Error loading suggestions</div>';
        this.showSuggestions();
    }
    
    renderSuggestions() {
        if (this.suggestions.length === 0) {
            this.showNoResults();
            return;
        }
        
        let html = '';
        
        // Add header with count and search info
        if (this.suggestions.length > 0) {
            const queryLength = this.searchInput.value.length;
            let searchType = '';
            if (queryLength === 1) searchType = ' (starting with)';
            else if (queryLength === 2) searchType = ' (name & company)';
            else searchType = ' (comprehensive)';
            
            html += `<div class="suggestions-header">${this.suggestions.length} product${this.suggestions.length !== 1 ? 's' : ''} found${searchType}</div>`;
        }
        
        this.suggestions.forEach((suggestion, index) => {
            const isActive = index === this.currentFocus ? 'active' : '';
            html += `
                <div class="suggestion-item ${isActive}" data-index="${index}">
                    <div class="suggestion-main">
                        <span class="product-name">${this.highlightMatch(suggestion.product_name, this.searchInput.value)}</span>
                        <span class="product-company">${suggestion.product_company}</span>
                    </div>
                    <div class="suggestion-details">
                        <span class="product-packing">${suggestion.product_packing}</span>
                        <span class="product-stock ${this.getStockClass(suggestion.current_stock)}">${suggestion.current_stock} units</span>
                    </div>
                </div>
            `;
        });
        
        this.suggestionsContainer.innerHTML = html;
        this.showSuggestions();
        this.bindSuggestionEvents();
    }
    
    bindSuggestionEvents() {
        const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectSuggestion(index);
            });
            
            item.addEventListener('mouseenter', () => {
                this.setActiveSuggestion(index);
            });
        });
    }
    
    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    getStockClass(stock) {
        if (stock <= 0) return 'stock-out';
        if (stock <= 10) return 'stock-low';
        return 'stock-good';
    }
    
    handleKeydown(e) {
        const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.currentFocus = Math.min(this.currentFocus + 1, items.length - 1);
                this.updateActiveSuggestion();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.currentFocus = Math.max(this.currentFocus - 1, -1);
                this.updateActiveSuggestion();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.currentFocus >= 0 && this.suggestions[this.currentFocus]) {
                    this.selectSuggestion(this.currentFocus);
                } else {
                    // Submit form if no suggestion selected
                    this.searchInput.closest('form')?.submit();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                this.searchInput.blur();
                break;
        }
    }
    
    setActiveSuggestion(index) {
        this.currentFocus = index;
        this.updateActiveSuggestion();
    }
    
    updateActiveSuggestion() {
        const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentFocus);
        });
    }
    
    selectSuggestion(index) {
        const suggestion = this.suggestions[index];
        if (suggestion) {
            this.searchInput.value = suggestion.product_name;
            this.hideSuggestions();
            
            // Trigger search
            this.searchInput.closest('form')?.submit();
        }
    }
    
    showSuggestions() {
        this.suggestionsContainer.style.display = 'block';
        this.suggestionsContainer.classList.add('show');
    }
    
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.suggestionsContainer.classList.remove('show');
        this.currentFocus = -1;
    }
    
    handleSortChange(sortValue) {
        // Update URL with sort parameter
        const url = new URL(window.location);
        if (sortValue) {
            url.searchParams.set('sort', sortValue);
        } else {
            url.searchParams.delete('sort');
        }
        
        // Preserve search query
        const searchQuery = this.searchInput.value;
        if (searchQuery) {
            url.searchParams.set('search', searchQuery);
        }
        
        // Reload page with new parameters
        window.location.href = url.toString();
    }
}

// Note: CSS styles are loaded from product-search-autocomplete.css

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize autocomplete for product search
    if (document.getElementById('product-search-input')) {
        new ProductSearchAutocomplete(
            'product-search-input',
            'search-suggestions',
            'sort-select'
        );
    }
});