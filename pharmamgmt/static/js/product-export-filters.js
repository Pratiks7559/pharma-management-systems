// Update export URLs with current filters
document.addEventListener('DOMContentLoaded', function() {
    const searchQuery = new URLSearchParams(window.location.search).get('search') || '';
    const sortBy = new URLSearchParams(window.location.search).get('sort') || '';
    
    const exportPdfBtns = document.querySelectorAll('[href*="export_products_pdf"]');
    const exportExcelBtns = document.querySelectorAll('[href*="export_products_excel"]');
    
    exportPdfBtns.forEach(btn => {
        const baseUrl = btn.getAttribute('href').split('?')[0];
        btn.setAttribute('href', `${baseUrl}?search=${searchQuery}&sort=${sortBy}`);
    });
    
    exportExcelBtns.forEach(btn => {
        const baseUrl = btn.getAttribute('href').split('?')[0];
        btn.setAttribute('href', `${baseUrl}?search=${searchQuery}&sort=${sortBy}`);
    });
});
