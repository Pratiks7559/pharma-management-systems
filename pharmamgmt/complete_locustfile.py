"""
Complete Locust Load Test - All Routes
Tests all major components of Pharmacy Management System
"""

from locust import HttpUser, task, between
import random

class CompletePharmacyTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login once per user"""
        response = self.client.get("/login/")
        csrf_token = response.cookies.get('csrftoken', '')
        self.client.post("/login/", {
            "username": "admin",
            "password": "admin",
            "csrfmiddlewaretoken": csrf_token
        }, catch_response=True)
    
    # ========== DASHBOARD ==========
    @task(10)
    def view_dashboard(self):
        """Test dashboard - most visited page"""
        self.client.get("/dashboard/")
    
    # ========== PRODUCTS ==========
    @task(8)
    def view_products(self):
        """Test product list"""
        self.client.get("/products/")
    
    @task(2)
    def search_products(self):
        """Test product search API"""
        self.client.get("/api/search-products/?q=paracetamol")
    
    @task(1)
    def product_suggestions(self):
        """Test product search suggestions"""
        self.client.get("/api/product-search-suggestions/?term=aspirin")
    
    # ========== INVENTORY ==========
    @task(6)
    def view_inventory(self):
        """Test inventory list"""
        self.client.get("/inventory/")
    
    @task(2)
    def batch_inventory_report(self):
        """Test batch inventory report"""
        self.client.get("/reports/inventory/batch/")
    
    @task(2)
    def expiry_inventory_report(self):
        """Test expiry inventory report"""
        self.client.get("/reports/inventory/expiry/")
    
    @task(1)
    def low_stock_update(self):
        """Test low stock page"""
        self.client.get("/inventory/low-stock-update/")
    
    # ========== SUPPLIERS ==========
    @task(5)
    def view_suppliers(self):
        """Test supplier list"""
        self.client.get("/suppliers/")
    
    @task(1)
    def search_suppliers(self):
        """Test supplier search"""
        self.client.get("/api/search-suppliers/?q=supplier")
    
    # ========== CUSTOMERS ==========
    @task(5)
    def view_customers(self):
        """Test customer list"""
        self.client.get("/customers/")
    
    @task(1)
    def search_customers(self):
        """Test customer search"""
        self.client.get("/api/search-customers/?q=customer")
    
    # ========== PURCHASE INVOICES ==========
    @task(7)
    def view_invoices(self):
        """Test purchase invoice list"""
        self.client.get("/invoices/")
    
    @task(2)
    def add_invoice_page(self):
        """Test add invoice page"""
        self.client.get("/invoices/add-with-products/")
    
    # ========== SALES INVOICES ==========
    @task(7)
    def view_sales(self):
        """Test sales invoice list"""
        self.client.get("/sales/")
    
    @task(2)
    def add_sales_page(self):
        """Test add sales page"""
        self.client.get("/sales/add-with-products/")
    
    # ========== CHALLANS ==========
    @task(3)
    def supplier_challans(self):
        """Test supplier challan list"""
        self.client.get("/challan/supplier/")
    
    @task(3)
    def customer_challans(self):
        """Test customer challan list"""
        self.client.get("/challan/customer/")
    
    # ========== RETURNS ==========
    @task(3)
    def purchase_returns(self):
        """Test purchase return list"""
        self.client.get("/purchase-returns/")
    
    @task(3)
    def sales_returns(self):
        """Test sales return list"""
        self.client.get("/sales-returns/")
    
    # ========== REPORTS ==========
    @task(4)
    def sales_report(self):
        """Test sales report"""
        self.client.get("/reports/sales/")
    
    @task(4)
    def purchase_report(self):
        """Test purchase report"""
        self.client.get("/reports/purchases/")
    
    @task(3)
    def sales2_report(self):
        """Test enhanced sales report"""
        self.client.get("/reports/sales2/")
    
    @task(3)
    def purchase2_report(self):
        """Test enhanced purchase report"""
        self.client.get("/reports/purchase2/")
    
    @task(2)
    def financial_report(self):
        """Test financial report"""
        self.client.get("/reports/financial/")
    
    @task(2)
    def stock_statement(self):
        """Test stock statement"""
        self.client.get("/reports/stock-statement/")
    
    @task(2)
    def customer_sales_report(self):
        """Test customer-wise sales report"""
        self.client.get("/reports/customer-sales/")
    
    # ========== LEDGER ==========
    @task(3)
    def ledger_selection(self):
        """Test ledger selection page"""
        self.client.get("/ledger/")
    
    @task(2)
    def customer_ledger(self):
        """Test customer ledger"""
        self.client.get("/ledger/customer/")
    
    @task(2)
    def supplier_ledger(self):
        """Test supplier ledger"""
        self.client.get("/ledger/supplier/")
    
    # ========== PAYMENTS & RECEIPTS ==========
    @task(3)
    def view_payments(self):
        """Test payment list"""
        self.client.get("/payments/")
    
    @task(2)
    def unified_payment(self):
        """Test unified payment form"""
        self.client.get("/finance/add/")
    
    @task(2)
    def view_receipts(self):
        """Test receipt list"""
        self.client.get("/receipts/")
    
    # ========== STOCK ISSUES ==========
    @task(2)
    def stock_issues(self):
        """Test stock issue list"""
        self.client.get("/stock-issues/")
    
    # ========== CONTRA ENTRIES ==========
    @task(2)
    def contra_list(self):
        """Test contra entry list"""
        self.client.get("/contra/")
    
    # ========== USERS ==========
    @task(1)
    def user_list(self):
        """Test user management"""
        self.client.get("/users/")
    
    @task(1)
    def profile(self):
        """Test user profile"""
        self.client.get("/profile/")
    
    # ========== PHARMACY DETAILS ==========
    @task(1)
    def pharmacy_details(self):
        """Test pharmacy details"""
        self.client.get("/pharmacy-details/")
    
    # ========== BACKUPS ==========
    @task(1)
    def backup_list(self):
        """Test backup management"""
        self.client.get("/system/backups/")


class QuickPublicTest(HttpUser):
    """Quick test for public pages - no login required"""
    wait_time = between(0.5, 2)
    
    @task
    def test_login_page(self):
        self.client.get("/login/")
    
    @task
    def test_home(self):
        self.client.get("/")


class APILoadTest(HttpUser):
    """Test API endpoints specifically"""
    wait_time = between(0.5, 1.5)
    
    @task(5)
    def search_products_api(self):
        terms = ["paracetamol", "aspirin", "amoxicillin", "ibuprofen", "cetirizine"]
        term = random.choice(terms)
        self.client.get(f"/api/search-products/?q={term}")
    
    @task(3)
    def product_suggestions_api(self):
        self.client.get("/api/product-search-suggestions/?term=para")
    
    @task(2)
    def search_suppliers_api(self):
        self.client.get("/api/search-suppliers/?q=supplier")
    
    @task(2)
    def search_customers_api(self):
        self.client.get("/api/search-customers/?q=customer")
    
    @task(1)
    def inventory_search_api(self):
        self.client.get("/api/inventory-search-suggestions/?term=batch")
