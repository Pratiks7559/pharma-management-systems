/**
 * Enhanced Sales Analytics JavaScript
 * Provides real-time data updates and interactive features
 */

class SalesAnalytics {
    constructor() {
        this.apiEndpoint = '/api/sales-analytics/';
        this.refreshInterval = 300000; // 5 minutes
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Date range form submission
        document.getElementById('dateRangeForm')?.addEventListener('submit', (e) => {
            this.showLoading();
        });

        // Quick range buttons
        document.querySelectorAll('.btn-quick').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const period = e.target.textContent.toLowerCase().replace(' ', '');
                this.setQuickRange(period);
            });
        });

        // Export buttons
        document.getElementById('exportPDF')?.addEventListener('click', () => this.exportToPDF());
        document.getElementById('exportExcel')?.addEventListener('click', () => this.exportToExcel());
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.refreshData());
    }

    setQuickRange(period) {
        const today = new Date();
        const startInput = document.getElementById('start_date');
        const endInput = document.getElementById('end_date');
        
        if (!startInput || !endInput) return;

        let startDate, endDate = new Date();

        switch(period) {
            case 'today':
                startDate = new Date();
                break;
            case 'thisweek':
                startDate = new Date(today.setDate(today.getDate() - today.getDay()));
                break;
            case 'thismonth':
                startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                break;
            case 'thisquarter':
                const quarter = Math.floor(today.getMonth() / 3);
                startDate = new Date(today.getFullYear(), quarter * 3, 1);
                break;
            default:
                return;
        }

        startInput.value = this.formatDate(startDate);
        endInput.value = this.formatDate(endDate);
        
        // Auto-submit form
        document.getElementById('dateRangeForm').submit();
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    async refreshData() {
        this.showLoading();
        
        try {
            const startDate = document.getElementById('start_date')?.value;
            const endDate = document.getElementById('end_date')?.value;
            
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            const response = await fetch(`${this.apiEndpoint}?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.updateKPIs(data.data);
                this.updateCharts(data.data);
                this.showSuccessMessage('Data refreshed successfully');
            } else {
                this.showErrorMessage('Failed to refresh data');
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showErrorMessage('Error refreshing data');
        } finally {
            this.hideLoading();
        }
    }

    updateKPIs(data) {
        // Update KPI values
        const kpiMappings = {
            'total_sales': data.core_metrics?.total_sales,
            'total_received': data.core_metrics?.total_received,
            'total_pending': data.core_metrics?.total_pending,
            'total_invoices': data.core_metrics?.total_invoices,
            'unique_customers': data.realtime_stats?.unique_customers,
            'total_products_sold': data.realtime_stats?.total_products_sold,
            'total_discount': data.realtime_stats?.total_discount_given,
            'total_tax': data.realtime_stats?.total_tax_collected
        };

        Object.entries(kpiMappings).forEach(([key, value]) => {
            const element = document.querySelector(`[data-kpi="${key}"]`);
            if (element && value !== undefined) {
                element.textContent = this.formatCurrency(value);
            }
        });
    }

    updateCharts(data) {
        // Update product chart
        if (this.charts.productChart && data.product_analytics) {
            const topProducts = data.product_analytics.slice(0, 8);
            this.charts.productChart.data.labels = topProducts.map(p => p.productid__product_name?.substring(0, 20));
            this.charts.productChart.data.datasets[0].data = topProducts.map(p => p.total_amount);
            this.charts.productChart.update();
        }

        // Update customer chart
        if (this.charts.customerChart && data.customer_analytics) {
            const topCustomers = data.customer_analytics.slice(0, 8);
            this.charts.customerChart.data.labels = topCustomers.map(c => c.sales_invoice_no__customerid__customer_name?.substring(0, 20));
            this.charts.customerChart.data.datasets[0].data = topCustomers.map(c => c.total_amount);
            this.charts.customerChart.update();
        }

        // Update daily trend chart
        if (this.charts.dailyChart && data.daily_trend) {
            this.charts.dailyChart.data.labels = data.daily_trend.map(d => new Date(d.day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            this.charts.dailyChart.data.datasets[0].data = data.daily_trend.map(d => d.daily_total);
            this.charts.dailyChart.update();
        }
    }

    initializeCharts() {
        // Chart configuration will be handled by the template
        // This method can be extended for dynamic chart creation
    }

    exportToPDF() {
        const startDate = document.getElementById('start_date')?.value || '';
        const endDate = document.getElementById('end_date')?.value || '';
        const url = `/export/sales/pdf/?start_date=${startDate}&end_date=${endDate}`;
        window.open(url, '_blank');
    }

    exportToExcel() {
        const startDate = document.getElementById('start_date')?.value || '';
        const endDate = document.getElementById('end_date')?.value || '';
        const url = `/export/sales/excel/?start_date=${startDate}&end_date=${endDate}`;
        window.open(url, '_blank');
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
        
        // Add loading class to refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        
        // Reset refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Data';
        }
    }

    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    formatCurrency(value) {
        if (typeof value !== 'number') return value;
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    formatNumber(value) {
        if (typeof value !== 'number') return value;
        return new Intl.NumberFormat('en-IN').format(value);
    }

    startAutoRefresh() {
        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.updateRealtimeIndicator();
        }, this.refreshInterval);
    }

    updateRealtimeIndicator() {
        const indicator = document.querySelector('.realtime-pulse');
        if (indicator) {
            indicator.style.animation = 'none';
            setTimeout(() => {
                indicator.style.animation = 'pulse 2s infinite';
            }, 100);
        }
    }
}

// Utility functions for global use
window.SalesAnalyticsUtils = {
    setQuickRange: function(period) {
        if (window.salesAnalytics) {
            window.salesAnalytics.setQuickRange(period);
        }
    },
    
    refreshAnalytics: function() {
        if (window.salesAnalytics) {
            window.salesAnalytics.refreshData();
        }
    },
    
    exportToPDF: function() {
        if (window.salesAnalytics) {
            window.salesAnalytics.exportToPDF();
        }
    },
    
    exportToExcel: function() {
        if (window.salesAnalytics) {
            window.salesAnalytics.exportToExcel();
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.salesAnalytics = new SalesAnalytics();
});

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
`;
document.head.appendChild(notificationStyles);