#!/usr/bin/env python
"""
Stock Issue Testing Script
Tests inventory updates when stock issues are created and deleted
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import (
    ProductMaster, InventoryMaster, StockIssueMaster, StockIssueDetail, 
    InventoryTransaction, SupplierMaster
)
from django.db import transaction
from django.utils import timezone

User = get_user_model()

class StockIssueTest:
    def __init__(self):
        self.test_user = None
        self.test_product = None
        self.test_inventory = None
        self.test_supplier = None
        
    def setup_test_data(self):
        """Create test data for stock issue testing"""
        print("🔧 Setting up test data...")
        
        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'password': 'test123',
                'user_type': 'admin',
                'user_contact': '1234567890'
            }
        )
        print(f"✅ Test user: {self.test_user.username}")
        
        # Create test supplier
        self.test_supplier, created = SupplierMaster.objects.get_or_create(
            supplier_name='Test Supplier',
            defaults={
                'supplier_mobile': '9876543210',
                'supplier_address': 'Test Address'
            }
        )
        print(f"✅ Test supplier: {self.test_supplier.supplier_name}")
        
        # Create test product
        self.test_product, created = ProductMaster.objects.get_or_create(
            product_name='Paracetamol Test',
            defaults={
                'product_company': 'Test Pharma',
                'product_packing': '10 TAB'
            }
        )
        print(f"✅ Test product: {self.test_product.product_name} (ID: {self.test_product.productid})")
        
        # Create test inventory
        self.test_inventory, created = InventoryMaster.objects.get_or_create(
            product=self.test_product,
            batch_no='TEST001',
            defaults={
                'expiry_date': '12-2025',
                'mrp': 50.0,
                'purchase_rate': 40.0,
                'current_stock': 100.0,
                'supplier': self.test_supplier
            }
        )
        
        if not created:
            # Reset stock to 100 for testing
            self.test_inventory.current_stock = 100.0
            self.test_inventory.save()
            
        print(f"✅ Test inventory: {self.test_inventory.product.product_name} - Batch: {self.test_inventory.batch_no} - Stock: {self.test_inventory.current_stock}")
        
    def test_stock_issue_creation(self):
        """Test stock issue creation and inventory update"""
        print("\n🧪 Testing Stock Issue Creation...")
        
        initial_stock = self.test_inventory.current_stock
        issue_quantity = 10.0
        
        print(f"📊 Initial stock: {initial_stock}")
        print(f"📤 Issue quantity: {issue_quantity}")
        
        try:
            with transaction.atomic():
                # Create stock issue
                issue = StockIssueMaster.objects.create(
                    issue_type='damage',
                    issue_date=timezone.now().date(),
                    remarks='Test stock issue',
                    created_by=self.test_user
                )
                issue.save()  # Generate issue_no
                
                print(f"✅ Stock issue created: {issue.issue_no}")
                
                # Update inventory
                inventory = InventoryMaster.objects.get(
                    product=self.test_product,
                    batch_no='TEST001'
                )
                
                if inventory.current_stock < issue_quantity:
                    raise ValueError(f"Insufficient stock. Available: {inventory.current_stock}, Required: {issue_quantity}")
                
                # Decrease stock
                inventory.current_stock = max(0, inventory.current_stock - issue_quantity)
                inventory.save()
                
                print(f"📉 Stock updated: {initial_stock} → {inventory.current_stock}")
                
                # Create inventory transaction
                transaction_record = InventoryTransaction.objects.create(
                    inventory=inventory,
                    transaction_type='adjustment',
                    quantity=-issue_quantity,
                    unit_rate=inventory.purchase_rate,
                    reference_type='stock_issue',
                    reference_id=issue.issue_no or f'SI-{issue.issue_id}',
                    remarks=f"Stock Issue: {issue.get_issue_type_display()} - Test",
                    created_by=self.test_user
                )
                
                print(f"📝 Transaction logged: ID {transaction_record.transaction_id}")
                
                # Create stock issue detail
                detail = StockIssueDetail.objects.create(
                    issue=issue,
                    product=self.test_product,
                    batch_no='TEST001',
                    expiry_date='12-2025',
                    quantity_issued=issue_quantity,
                    unit_rate=inventory.purchase_rate,
                    remarks='Test issue detail'
                )
                
                print(f"📋 Issue detail created: {detail.detail_id}")
                
                # Verify stock decrease
                updated_inventory = InventoryMaster.objects.get(
                    product=self.test_product,
                    batch_no='TEST001'
                )
                
                expected_stock = initial_stock - issue_quantity
                actual_stock = updated_inventory.current_stock
                
                if actual_stock == expected_stock:
                    print(f"✅ PASS: Stock correctly decreased from {initial_stock} to {actual_stock}")
                    return issue, True
                else:
                    print(f"❌ FAIL: Expected stock {expected_stock}, but got {actual_stock}")
                    return issue, False
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None, False
    
    def test_stock_issue_deletion(self, issue):
        """Test stock issue deletion and inventory reversal"""
        print("\n🧪 Testing Stock Issue Deletion...")
        
        if not issue:
            print("❌ No issue to delete")
            return False
            
        try:
            # Get current stock before deletion
            inventory_before = InventoryMaster.objects.get(
                product=self.test_product,
                batch_no='TEST001'
            )
            stock_before = inventory_before.current_stock
            
            print(f"📊 Stock before deletion: {stock_before}")
            
            with transaction.atomic():
                # Get issue details
                details = issue.details.all()
                total_quantity_to_restore = sum(detail.quantity_issued for detail in details)
                
                print(f"📤 Quantity to restore: {total_quantity_to_restore}")
                
                # Reverse inventory changes
                for detail in details:
                    inventory = InventoryMaster.objects.get(
                        product=detail.product,
                        batch_no=detail.batch_no
                    )
                    
                    # Add back the issued quantity
                    inventory.current_stock += detail.quantity_issued
                    inventory.save()
                    
                    # Create reversal transaction
                    InventoryTransaction.objects.create(
                        inventory=inventory,
                        transaction_type='adjustment',
                        quantity=detail.quantity_issued,
                        unit_rate=detail.unit_rate,
                        reference_type='stock_issue_reversal',
                        reference_id=issue.issue_no,
                        remarks=f"Stock Issue Reversal: {issue.get_issue_type_display()} - Deleted",
                        created_by=self.test_user
                    )
                
                # Delete the issue
                issue_no = issue.issue_no
                issue.delete()
                
                print(f"🗑️ Issue deleted: {issue_no}")
                
                # Verify stock restoration
                inventory_after = InventoryMaster.objects.get(
                    product=self.test_product,
                    batch_no='TEST001'
                )
                stock_after = inventory_after.current_stock
                
                expected_stock = stock_before + total_quantity_to_restore
                
                if stock_after == expected_stock:
                    print(f"✅ PASS: Stock correctly restored from {stock_before} to {stock_after}")
                    return True
                else:
                    print(f"❌ FAIL: Expected stock {expected_stock}, but got {stock_after}")
                    return False
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_inventory_transactions(self):
        """Test inventory transaction logging"""
        print("\n🧪 Testing Inventory Transactions...")
        
        try:
            # Get all transactions for our test inventory
            transactions = InventoryTransaction.objects.filter(
                inventory=self.test_inventory
            ).order_by('-transaction_date')
            
            print(f"📝 Total transactions found: {transactions.count()}")
            
            for i, trans in enumerate(transactions[:5], 1):  # Show last 5 transactions
                print(f"  {i}. {trans.transaction_type} | Qty: {trans.quantity} | Ref: {trans.reference_type} | Date: {trans.transaction_date.strftime('%Y-%m-%d %H:%M')}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def test_batch_stock_status(self):
        """Test batch stock status function"""
        print("\n🧪 Testing Batch Stock Status...")
        
        try:
            from core.views import get_batch_stock_status
            
            current_stock, is_available = get_batch_stock_status(
                self.test_product.productid, 
                'TEST001'
            )
            
            # Get actual stock from database
            actual_inventory = InventoryMaster.objects.get(
                product=self.test_product,
                batch_no='TEST001'
            )
            
            print(f"📊 Function returned: Stock={current_stock}, Available={is_available}")
            print(f"📊 Database shows: Stock={actual_inventory.current_stock}")
            
            if current_stock == actual_inventory.current_stock:
                print("✅ PASS: Batch stock status function working correctly")
                return True
            else:
                print("❌ FAIL: Batch stock status function returning incorrect values")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all stock issue tests"""
        print("🚀 Starting Stock Issue Tests")
        print("=" * 50)
        
        # Setup
        self.setup_test_data()
        
        # Test 1: Stock Issue Creation
        issue, creation_success = self.test_stock_issue_creation()
        
        # Test 2: Inventory Transactions
        transaction_success = self.test_inventory_transactions()
        
        # Test 3: Batch Stock Status
        batch_status_success = self.test_batch_stock_status()
        
        # Test 4: Stock Issue Deletion
        deletion_success = self.test_stock_issue_deletion(issue) if issue else False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Stock Issue Creation: {'✅ PASS' if creation_success else '❌ FAIL'}")
        print(f"Inventory Transactions: {'✅ PASS' if transaction_success else '❌ FAIL'}")
        print(f"Batch Stock Status: {'✅ PASS' if batch_status_success else '❌ FAIL'}")
        print(f"Stock Issue Deletion: {'✅ PASS' if deletion_success else '❌ FAIL'}")
        
        all_passed = all([creation_success, transaction_success, batch_status_success, deletion_success])
        print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '⚠️ SOME TESTS FAILED'}")
        
        return all_passed

if __name__ == "__main__":
    tester = StockIssueTest()
    tester.run_all_tests()