/**
 * Enhanced Financial Report JavaScript
 * Provides interactive functionality for the financial report
 */

class FinancialReport {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.setupAutoRefresh();
        this.addAnimations();
    }

    setupEventListeners() {
        // Date range form submission
        const dateForm = document.querySelector('.financial-date-range-form');
        if (dateForm) {
            dateForm.addEventListener('submit', this.handleDateRangeSubmit.bind(this));
        }

        // Export buttons
        document.querySelectorAll('.financial-export-btn').forEach(btn => {
            btn.addEventListener('click', this.handleExport.bind(this));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Window resize for responsive charts
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    handleDateRangeSubmit(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const startDate = formData.get('start_date');
        const endDate = formData.get('end_date');

        if (startDate && endDate) {
            if (new Date(startDate) > new Date(endDate)) {
                this.showNotification('Start date cannot be after end date', 'error');
                return;
            }

            this.showLoading();
            window.location.href = `${window.location.pathname}?start_date=${startDate}&end_date=${endDate}`;
        }
    }

    handleExport(event) {
        const btn = event.currentTarget;
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        btn.style.pointerEvents = 'none';

        // Reset button after 3 seconds
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.pointerEvents = 'auto';
        }, 3000);
    }

    handleKeyboardShortcuts(event) {
        // Ctrl+P for print
        if (event.ctrlKey && event.key === 'p') {
            event.preventDefault();
            window.print();
        }

        // Ctrl+E for Excel export
        if (event.ctrlKey && event.key === 'e') {
            event.preventDefault();
            const excelBtn = document.querySelector('.financial-export-excel');
            if (excelBtn) excelBtn.click();
        }

        // Ctrl+R for refresh
        if (event.ctrlKey && event.key === 'r') {
            event.preventDefault();
            this.refreshData();
        }
    }

    handleResize() {
        // Debounce resize events
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.resize === 'function') {
                    chart.resize();
                }
            });
        }, 250);
    }

    initializeCharts() {
        this.initializeSalesChart();
        this.initializeCashFlowChart();
        this.initializeProfitChart();
    }

    initializeSalesChart() {
        const ctx = document.getElementById('monthlySalesChart');
        if (!ctx) return;

        const chartData = this.getChartData('sales');
        
        this.charts.sales = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Sales',
                    data: chartData.sales,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Purchases',
                    data: chartData.purchases,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    initializeCashFlowChart() {
        const ctx = document.getElementById('cashFlowChart');
        if (!ctx) return;

        const chartData = this.getChartData('cashflow');
        
        this.charts.cashflow = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Cash Inflow',
                    data: chartData.inflow,
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2,
                    borderRadius: 4
                }, {
                    label: 'Cash Outflow',
                    data: chartData.outflow,
                    backgroundColor: 'rgba(220, 53, 69, 0.8)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 2,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutBounce'
                }
            }
        });
    }

    initializeProfitChart() {
        // Initialize profit trend chart if element exists
        const ctx = document.getElementById('profitChart');
        if (!ctx) return;

        // Implementation for profit chart
        // This would be similar to other charts
    }

    getChartData(type) {
        // Extract chart data from DOM or make AJAX call
        // This is a placeholder - in real implementation, 
        // data would come from the Django template or API
        
        switch(type) {
            case 'sales':
                return {
                    labels: window.chartData?.monthlyLabels || [],
                    sales: window.chartData?.monthlySales || [],
                    purchases: window.chartData?.monthlyPurchases || []
                };
            case 'cashflow':
                return {
                    labels: window.chartData?.cashFlowLabels || [],
                    inflow: window.chartData?.inflowData || [],
                    outflow: window.chartData?.outflowData || []
                };
            default:
                return { labels: [], data: [] };
        }
    }

    setupAutoRefresh() {
        // Auto-refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 300000); // 5 minutes
    }

    refreshData() {
        const url = document.querySelector('[data-financial-api]')?.dataset.financialApi || '/api/financial-dashboard/';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                this.updateMetrics(data);
                this.showNotification('Data refreshed successfully', 'success');
            })
            .catch(error => {
                console.error('Error refreshing data:', error);
                this.showNotification('Failed to refresh data', 'error');
            });
    }

    updateMetrics(data) {
        // Update key metrics without full page reload
        const metrics = {
            'sales': data.sales,
            'purchases': data.purchases,
            'gross_profit': data.gross_profit,
            'total_receivables': data.total_receivables,
            'total_payables': data.total_payables
        };

        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.querySelector(`[data-metric="${key}"]`);
            if (element) {
                this.animateValue(element, parseFloat(element.textContent.replace(/[₹,]/g, '')), value);
            }
        });
    }

    animateValue(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * this.easeOutQuart(progress);
            element.textContent = '₹' + current.toLocaleString(undefined, {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            });
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    addAnimations() {
        // Add entrance animations to cards
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.financial-summary-card, .financial-kpi-card, .financial-chart-card').forEach(card => {
            observer.observe(card);
        });
    }

    showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin fa-3x"></i>
                <p>Loading financial data...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    destroy() {
        // Cleanup
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Enhanced DataTables configuration
function initializeDataTables() {
    const tableConfig = {
        responsive: true,
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            paginate: {
                first: "First",
                last: "Last",
                next: "Next",
                previous: "Previous"
            }
        },
        dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>' +
             '<"row"<"col-sm-12"tr>>' +
             '<"row"<"col-sm-5"i><"col-sm-7"p>>',
        drawCallback: function() {
            // Add animations to new rows
            $(this.api().table().node()).find('tbody tr').addClass('fade-in');
        }
    };

    // Initialize all financial tables
    $('#receivablesTable, #payablesTable').DataTable({
        ...tableConfig,
        order: [[1, "desc"]], // Sort by amount descending
        columnDefs: [{
            targets: 1,
            render: function(data, type, row) {
                if (type === 'display') {
                    return '₹' + parseFloat(data).toLocaleString();
                }
                return data;
            }
        }]
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize financial report
    window.financialReport = new FinancialReport();
    
    // Initialize DataTables
    initializeDataTables();
    
    // Add print styles
    const printStyles = `
        <style media="print">
            .no-print { display: none !important; }
            .financial-chart-area { height: 300px !important; }
            .financial-report-container { padding: 0 !important; }
        </style>
    `;
    document.head.insertAdjacentHTML('beforeend', printStyles);
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.financialReport) {
        window.financialReport.destroy();
    }
});

// Export for use in other scripts
window.FinancialReport = FinancialReport;