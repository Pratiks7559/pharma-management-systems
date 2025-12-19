"""
Locust Load Test for Pharmacy Management System
Run: locust -f locustfile.py
Then open: http://localhost:8089
"""

from locust import HttpUser, task, between

class PharmaUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when user starts - simulate login"""
        # Get login page
        response = self.client.get("/login/")
        
        # Try to login (will fail if no test user, but that's ok for testing)
        csrf_token = response.cookies.get('csrftoken', '')
        self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass123",
            "csrfmiddlewaretoken": csrf_token
        })
    
    @task(3)  # Weight: 3 (runs 3x more than others)
    def view_login_page(self):
        """Test login page load"""
        self.client.get("/login/")
    
    @task(2)
    def view_home(self):
        """Test home page"""
        self.client.get("/")
    
    @task(1)
    def view_dashboard(self):
        """Test dashboard (may redirect if not logged in)"""
        self.client.get("/dashboard/")
    
    @task(1)
    def view_products(self):
        """Test products page"""
        self.client.get("/products/")
    
    @task(1)
    def view_invoices(self):
        """Test invoices page"""
        self.client.get("/invoices/")
    
    @task(1)
    def view_sales(self):
        """Test sales page"""
        self.client.get("/sales-invoices/")
    
    @task(1)
    def view_customers(self):
        """Test customers page"""
        self.client.get("/customers/")


class QuickLoadTest(HttpUser):
    """Quick test - only public pages"""
    wait_time = between(0.5, 2)
    
    @task
    def quick_test(self):
        self.client.get("/login/")
        self.client.get("/")
